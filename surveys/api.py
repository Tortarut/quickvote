from rest_framework import viewsets, permissions, decorators, response, status
from django.utils import timezone
from django.shortcuts import get_object_or_404

from responses.views import build_statistics_payload
from .models import Survey, SurveyTemplate
from .serializers import SurveySerializer, SurveyPublicSerializer, SurveyTemplateSerializer


class IsAuthorOrAdmin(permissions.BasePermission):
    """Разрешение: только автор или администратор могут изменять опрос."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff


class SurveyViewSet(viewsets.ModelViewSet):
    """ViewSet для управления опросами через API."""
    serializer_class = SurveySerializer
    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrAdmin]

    def get_queryset(self):
        if self.action == "retrieve" and self.request.method == "GET":
            return Survey.objects.all()
        if self.request.user.is_staff:
            return Survey.objects.all()
        if not self.request.user.is_authenticated:
            return Survey.objects.filter(status=Survey.STATUS_ACTIVE)
        return Survey.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @decorators.action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny], url_path="public")
    def public(self, request, slug=None):
        survey = self.get_object()
        serializer = SurveyPublicSerializer(survey)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def close(self, request, slug=None):
        """Закрывает опрос (доступно только автору или администратору)."""
        survey = self.get_object()
        if survey.author != request.user and not request.user.is_staff:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        survey.status = Survey.STATUS_CLOSED
        survey.save(update_fields=["status"])
        return response.Response({"status": "closed"})

    @decorators.action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated], url_path="statistics")
    def statistics(self, request, slug=None):
        """Возвращает статистику опроса (доступно только автору или администратору)."""
        survey = self.get_object()
        if survey.author != request.user and not request.user.is_staff:
            return response.Response(status=status.HTTP_403_FORBIDDEN)
        payload = build_statistics_payload(survey)
        return response.Response(payload)


class SurveyTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра шаблонов опросов."""
    queryset = SurveyTemplate.objects.all()
    serializer_class = SurveyTemplateSerializer
    permission_classes = [permissions.AllowAny]

    @decorators.action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated], url_path="instantiate")
    def instantiate(self, request, pk=None):
        """Создает новый опрос на основе шаблона."""
        template = self.get_object()
        payload = template.payload
        serializer = SurveySerializer(
            data={
                "title": payload.get("title", template.title),
                "description": payload.get("description", template.description),
                "survey_type": payload.get("survey_type", Survey.TYPE_ANONYMOUS),
                "ends_at": payload.get("ends_at"),
                "questions": payload.get("questions", []),
                "welcome_message": payload.get("welcome_message", ""),
                "thank_you_message": payload.get("thank_you_message", ""),
                "theme": payload.get("theme", "light"),
            },
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        survey = serializer.save()
        survey.is_template_based = True
        survey.save(update_fields=["is_template_based"])
        return response.Response(SurveySerializer(survey).data, status=status.HTTP_201_CREATED)


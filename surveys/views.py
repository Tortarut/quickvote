from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, View
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from .models import Survey, SurveyTemplate


class SurveyListView(LoginRequiredMixin, TemplateView):
    """Список всех опросов текущего пользователя."""
    template_name = "surveys/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["surveys"] = Survey.objects.filter(author=self.request.user)
        context["base_url"] = self.request.build_absolute_uri("/")
        return context


class SurveyBuilderView(LoginRequiredMixin, TemplateView):
    """Страница конструктора опросов с доступом к шаблонам."""
    template_name = "surveys/builder.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["templates"] = SurveyTemplate.objects.all()
        return context


class SurveyDetailView(LoginRequiredMixin, DetailView):
    """Детальная страница опроса со статистикой."""
    model = Survey
    template_name = "surveys/detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Survey.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["base_url"] = self.request.build_absolute_uri("/")
        return context


class SurveyEditView(LoginRequiredMixin, TemplateView):
    """Редактирование опроса (только описание и дата окончания, если есть ответы)."""
    template_name = "surveys/edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["survey"] = get_object_or_404(Survey, slug=self.kwargs["slug"], author=self.request.user)
        return context

    def post(self, request, **kwargs):
        survey = get_object_or_404(Survey, slug=kwargs["slug"], author=request.user)
        survey.description = request.POST.get("description", "")
        ends_at = request.POST.get("ends_at")
        if ends_at:
            dt = parse_datetime(ends_at)
            if dt:
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
                survey.ends_at = dt
        else:
            survey.ends_at = None
        survey.save(update_fields=["description", "ends_at"])
        messages.success(request, "Опрос обновлен")
        return redirect("surveys:edit", slug=survey.slug)


class SurveyDeleteView(LoginRequiredMixin, TemplateView):
    """Удаление опроса с подтверждением."""
    template_name = "surveys/delete_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["survey"] = get_object_or_404(Survey, slug=self.kwargs["slug"], author=self.request.user)
        return context

    def post(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug, author=request.user)
        survey.delete()
        messages.success(request, "Опрос удален")
        return redirect("surveys:list")


class SurveyPublicView(TemplateView):
    """Публичная страница опроса для заполнения."""
    template_name = "surveys/public.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["survey"] = get_object_or_404(Survey, slug=self.kwargs["slug"])
        return context


class SurveyTemplatesView(TemplateView):
    """Страница со списком доступных шаблонов опросов."""
    template_name = "surveys/templates.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["templates"] = SurveyTemplate.objects.all()
        return context

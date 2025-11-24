import csv
import io
from collections import Counter

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.utils import timezone

from rest_framework import permissions, status, views
from rest_framework.response import Response

from surveys.models import Survey, Question
from .models import SurveyResponse
from .serializers import SurveyResponseSerializer


def build_statistics_payload(survey):
    """Строит статистику по опросу: подсчет ответов по типам вопросов."""
    data = []
    for question in survey.questions.all():
        question_data = {"id": question.id, "text": question.text, "type": question.question_type}
        answers = question.answer_set.all()
        if question.question_type in {Question.TYPE_SINGLE, Question.TYPE_MULTIPLE}:
            counts = Counter()
            for answer in answers:
                for choice in answer.selected_choices.all():
                    counts[choice.label] += 1
            total = sum(counts.values()) or 1
            question_data["options"] = [
                {"label": label, "count": count, "percentage": round(count / total * 100, 2)}
                for label, count in counts.items()
            ]
        elif question.question_type == Question.TYPE_TEXT:
            question_data["responses"] = [answer.text_answer for answer in answers if answer.text_answer]
        else:
            ratings = [answer.rating_value for answer in answers if answer.rating_value]
            avg = round(sum(ratings) / len(ratings), 2) if ratings else 0
            distribution = Counter(ratings)
            question_data["average"] = avg
            question_data["distribution"] = [{"rating": rating, "count": count} for rating, count in distribution.items()]
        data.append(question_data)
    return {"questions": data, "total_responses": survey.responses.count()}


class ThankYouView(TemplateView):
    """Страница благодарности после отправки ответа на опрос."""
    template_name = "responses/thank_you.html"


class SubmitResponseAPIView(views.APIView):
    """API endpoint для отправки ответа на опрос. Проверяет дубликаты."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        if not survey.is_active:
            return Response({"detail": "Опрос недоступен"}, status=status.HTTP_400_BAD_REQUEST)

        if self._is_duplicate_vote(request, survey):
            return Response({"detail": "Вы уже голосовали в этом опросе"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SurveyResponseSerializer(data=request.data, context={"survey": survey, "request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Спасибо за участие", "thank_you": survey.thank_you_message}, status=status.HTTP_201_CREATED)

    def _is_duplicate_vote(self, request, survey):
        """Проверяет, отвечал ли авторизованный пользователь уже на этот опрос."""
        if request.user.is_authenticated:
            return SurveyResponse.objects.filter(survey=survey, user=request.user).exists()
        return False


class SurveyStatisticsAPIView(views.APIView):
    """API endpoint для получения статистики опроса. Доступ только после участия."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        survey = get_object_or_404(Survey, slug=slug)
        if survey.author != request.user:
            has_participated = False
            if request.user.is_authenticated:
                has_participated = SurveyResponse.objects.filter(survey=survey, user=request.user).exists()
            if not has_participated and survey.survey_type != Survey.TYPE_PUBLIC:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if not has_participated and survey.survey_type == Survey.TYPE_PUBLIC:
                return Response(status=status.HTTP_403_FORBIDDEN)

        payload = build_statistics_payload(survey)
        return Response(payload)


class SurveyExportView(views.APIView):
    """API endpoint для экспорта результатов опроса в JSON или CSV."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug, fmt):
        survey = get_object_or_404(Survey, slug=slug)
        if survey.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if fmt == "json":
            payload = build_statistics_payload(survey)
            return Response(payload)
        elif fmt == "csv":
            return self._export_csv(survey)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def _export_csv(self, survey):
        """Экспортирует результаты опроса в CSV формат."""
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Вопрос", "Тип", "Ответ"])
        for question in survey.questions.all():
            answers = question.answer_set.all()
            for answer in answers:
                value = ""
                if question.question_type in {Question.TYPE_SINGLE, Question.TYPE_MULTIPLE}:
                    value = ", ".join(answer.selected_choices.values_list("label", flat=True))
                elif question.question_type == Question.TYPE_TEXT:
                    value = answer.text_answer
                else:
                    value = answer.rating_value
                writer.writerow([question.text, question.get_question_type_display(), value])
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{survey.slug}.csv"'
        return response

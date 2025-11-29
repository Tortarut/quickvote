from django.db import models
from django.conf import settings

from surveys.models import Survey, Question, Choice


class SurveyResponse(models.Model):
    """Модель ответа на опрос. Один пользователь может ответить на опрос только один раз."""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_anonymous = models.BooleanField(default=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-submitted_at"]
        unique_together = ("survey", "user")  # Один ответ от одного пользователя на опрос

    def __str__(self):
        return f"{self.survey.title} response {self.pk}"


class Answer(models.Model):
    """Модель ответа на конкретный вопрос в рамках SurveyResponse."""
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True)
    rating_value = models.PositiveSmallIntegerField(null=True, blank=True)
    selected_choices = models.ManyToManyField(Choice, blank=True)

    def __str__(self):
        return f"{self.question.text[:40]}"

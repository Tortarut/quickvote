from django.db import models

from surveys.models import Survey, Question


class SurveyAnalyticsSnapshot(models.Model):
    """Снимок аналитики опроса на момент времени."""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="analytics_snapshots")
    total_participants = models.PositiveIntegerField(default=0)
    average_completion_seconds = models.FloatField(default=0)
    completion_rate = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class QuestionCorrelation(models.Model):
    """Корреляция между ответами на два вопроса в опросе."""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    question_a = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="correlation_a")
    question_b = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="correlation_b")
    correlation_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("survey", "question_a", "question_b")

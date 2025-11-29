from django.db import models
from django.conf import settings

from surveys.models import Survey


class NotificationRule(models.Model):
    """Правило уведомления: отправка email при достижении порога ответов на опрос."""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="notification_rules")
    threshold = models.PositiveIntegerField(help_text="Количество ответов для уведомления")
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.survey.title}: {self.threshold}"


class Notification(models.Model):
    """Модель отправленного уведомления по правилу."""
    rule = models.ForeignKey(NotificationRule, on_delete=models.CASCADE, related_name="notifications")
    sent_at = models.DateTimeField(auto_now_add=True)
    total_responses = models.PositiveIntegerField(default=0)
    message = models.TextField()


class Complaint(models.Model):
    """Модель жалобы на опрос от пользователя."""
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="complaints")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

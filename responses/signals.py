from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone

from .models import SurveyResponse
from notifications.models import Notification, NotificationRule


@receiver(post_save, sender=SurveyResponse)
def on_response_created(sender, instance: SurveyResponse, created, **kwargs):
    """
    Сигнал: обработка создания ответа на опрос.
    Отправляет уведомления при достижении порога ответов и предупреждает о скором окончании опроса.
    """
    if not created:
        return
    survey = instance.survey
    total = survey.responses.count()

    for rule in survey.notification_rules.all():
        already_sent = rule.notifications.filter(total_responses__gte=rule.threshold).exists()
        if total >= rule.threshold and not already_sent:
            Notification.objects.create(
                rule=rule,
                total_responses=total,
                message=f"Опрос '{survey.title}' достиг {total} ответов",
            )
            send_mail(
                subject="QuickVote: достигнут порог ответов",
                message=f"Опрос '{survey.title}' набрал {total} ответов.",
                from_email=None,
                recipient_list=[rule.email],
            )

    if survey.ends_at:
        time_left = survey.ends_at - timezone.now()
        if timedelta(0) < time_left <= timedelta(hours=12):
            send_mail(
                subject="QuickVote: опрос скоро завершится",
                message=f"До окончания опроса '{survey.title}' осталось {time_left}.",
                from_email=None,
                recipient_list=[survey.author.email],
            )


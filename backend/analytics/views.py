from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Count

from surveys.models import Survey
from responses.models import SurveyResponse
from users.models import User


class DashboardView(LoginRequiredMixin, TemplateView):
    """Дашборд пользователя: статистика по опросам и последние ответы."""
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        surveys = Survey.objects.filter(author=self.request.user)
        responses = SurveyResponse.objects.filter(survey__author=self.request.user)
        context["surveys"] = surveys
        context["responses"] = responses
        context["active_surveys"] = surveys.filter(status=Survey.STATUS_ACTIVE).count()
        context["responses_count"] = responses.count()
        context["participants"] = responses.values("user").distinct().count()
        context["recent_responses"] = responses[:10]
        return context


class AdminMonitorView(UserPassesTestMixin, TemplateView):
    """Админ-панель: общая статистика по системе (только для staff)."""
    template_name = "dashboard/admin_monitor.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users_count"] = User.objects.count()
        context["active_surveys"] = Survey.objects.filter(status=Survey.STATUS_ACTIVE).count()
        context["votes_last_7_days"] = SurveyResponse.objects.filter(
            submitted_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        context["top_surveys"] = (
            Survey.objects.annotate(votes=Count("responses"))
            .order_by("-votes")[:5]
        )
        return context

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .forms import NotificationRuleForm, ComplaintForm
from .models import NotificationRule, Complaint


class NotificationCenterView(LoginRequiredMixin, TemplateView):
    """Центр уведомлений: управление правилами уведомлений и отправка жалоб."""
    template_name = "notifications/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rules"] = NotificationRule.objects.filter(survey__author=self.request.user)
        context["form"] = NotificationRuleForm(user=self.request.user)
        context["complaint_form"] = ComplaintForm()
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get("form_type", "rule")
        if form_type == "complaint":
            complaint_form = ComplaintForm(request.POST)
            if complaint_form.is_valid():
                complaint = complaint_form.save(commit=False)
                complaint.reporter = request.user
                complaint.save()
                messages.success(request, "Жалоба отправлена модератору")
            else:
                messages.error(request, "Не удалось отправить жалобу")
        else:
            form = NotificationRuleForm(request.POST, user=request.user)
            if form.is_valid():
                rule = form.save(commit=False)
                if rule.survey.author != request.user:
                    messages.error(request, "Можно добавлять уведомления только к своим опросам")
                else:
                    rule.save()
                    messages.success(request, "Правило уведомления создано")
            else:
                messages.error(request, "Исправьте ошибки в форме")
        return redirect("notifications:center")


class ComplaintListView(UserPassesTestMixin, TemplateView):
    """Список жалоб на опросы (только для staff)."""
    template_name = "notifications/complaints.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["complaints"] = Complaint.objects.all()
        context["form"] = ComplaintForm()
        return context

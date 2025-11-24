from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import FormView, UpdateView, TemplateView, View
from django.core.mail import send_mail

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response

from .forms import (
    RegistrationForm,
    LoginForm,
    ProfileForm,
    EmailChangeForm,
    PasswordUpdateForm,
)
from .models import User, EmailChangeRequest
from .serializers import UserSerializer, RegistrationSerializer, LoginSerializer


class LandingPageView(TemplateView):
    """Главная страница приложения."""
    template_name = "landing.html"


class RegisterView(FormView):
    """Регистрация нового пользователя."""
    template_name = "auth/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Регистрация прошла успешно")
        return super().form_valid(form)


class LoginView(FormView):
    """Вход в систему с поддержкой "запомнить меня"."""
    template_name = "auth/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        user = form.cleaned_data["user"]
        login(self.request, user)
        remember = form.cleaned_data.get("remember_me")
        if remember:
            self.request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            self.request.session.set_expiry(0)
        messages.success(self.request, "Вы вошли в систему")
        return super().form_valid(form)


class LogoutView(View):
    """Выход из системы."""
    def get(self, request):
        logout(request)
        return redirect("home")


class ProfileView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""
    template_name = "auth/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль обновлен")
        return super().form_valid(form)


class EmailChangeRequestView(LoginRequiredMixin, FormView):
    """Запрос на смену email с отправкой подтверждения на новый адрес."""
    template_name = "auth/email_change.html"
    form_class = EmailChangeForm
    success_url = reverse_lazy("users:profile")

    def form_valid(self, form):
        new_email = form.cleaned_data["new_email"]
        expires_at = timezone.now() + timedelta(hours=24)
        request_obj = EmailChangeRequest.objects.create(
            user=self.request.user,
            new_email=new_email,
            expires_at=expires_at,
        )
        confirmation_url = self.request.build_absolute_uri(
            reverse("users:confirm-email-change", args=[request_obj.token])
        )
        send_mail(
            subject="Подтверждение нового email",
            message=f"Для подтверждения перейдите по ссылке: {confirmation_url}",
            from_email=None,
            recipient_list=[new_email],
        )
        messages.info(self.request, "Мы отправили ссылку на новый email")
        return super().form_valid(form)


class ConfirmEmailChangeView(View):
    """Подтверждение смены email по токену из письма."""
    def get(self, request, token):
        change_request = get_object_or_404(EmailChangeRequest, token=token, confirmed=False)
        if change_request.is_expired():
            messages.error(request, "Ссылка устарела")
            return redirect("users:profile")
        user = change_request.user
        user.email = change_request.new_email
        user.email_confirmed = True
        user.save(update_fields=["email", "email_confirmed"])
        change_request.confirmed = True
        change_request.save(update_fields=["confirmed"])
        messages.success(request, "Email успешно обновлен")
        return redirect("users:profile")


class PasswordUpdateView(LoginRequiredMixin, FormView):
    """Смена пароля с проверкой текущего пароля."""
    template_name = "auth/password_change.html"
    form_class = PasswordUpdateForm
    success_url = reverse_lazy("users:profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        new_password = form.cleaned_data["new_password"]
        self.request.user.set_password(new_password)
        self.request.user.save()
        messages.success(self.request, "Пароль обновлен")
        return super().form_valid(form)


class ResetPasswordRequestView(PasswordResetView):
    """Запрос на сброс пароля."""
    template_name = "auth/password_reset_request.html"
    email_template_name = "emails/password_reset_email.txt"
    success_url = reverse_lazy("users:password-reset-request")


class PasswordResetConfirm(PasswordResetConfirmView):
    """Подтверждение сброса пароля по токену."""
    template_name = "auth/password_reset_confirm.html"
    success_url = reverse_lazy("users:login")


class UserHistoryView(LoginRequiredMixin, TemplateView):
    """История пользователя: созданные опросы и данные ответов."""
    template_name = "auth/history.html"

    def get_context_data(self, **kwargs):
        from surveys.models import Survey
        from responses.models import SurveyResponse

        context = super().get_context_data(**kwargs)
        context["created_surveys"] = Survey.objects.filter(author=self.request.user)
        context["responses"] = SurveyResponse.objects.filter(user=self.request.user)
        return context


# API views
class RegisterAPIView(generics.CreateAPIView):
    """API endpoint для регистрации пользователя."""
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        login(self.request, user)


class LoginAPIView(views.APIView):
    """API endpoint для входа в систему."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        remember = serializer.validated_data.get("remember_me")
        if remember:
            request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            request.session.set_expiry(0)
        return Response(UserSerializer(user).data)


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """API endpoint для просмотра и обновления профиля пользователя."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    EmailChangeRequestView,
    ConfirmEmailChangeView,
    PasswordUpdateView,
    ResetPasswordRequestView,
    PasswordResetConfirm,
    UserHistoryView,
    RegisterAPIView,
    LoginAPIView,
    ProfileAPIView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/email-change/", EmailChangeRequestView.as_view(), name="email-change"),
    path("profile/email-change/<uuid:token>/", ConfirmEmailChangeView.as_view(), name="confirm-email-change"),
    path("profile/password/", PasswordUpdateView.as_view(), name="password-change"),
    path("history/", UserHistoryView.as_view(), name="history"),
    path("password-reset/", ResetPasswordRequestView.as_view(), name="password-reset-request"),
    path("password-reset-confirm/<uidb64>/<token>/", PasswordResetConfirm.as_view(), name="password_reset_confirm"),
    path("api/register/", RegisterAPIView.as_view(), name="api-register"),
    path("api/login/", LoginAPIView.as_view(), name="api-login"),
    path("api/profile/", ProfileAPIView.as_view(), name="api-profile"),
]


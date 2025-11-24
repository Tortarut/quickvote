import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone


class User(AbstractUser):
    """Расширенная модель пользователя с дополнительными полями."""
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z0-9_.-]{3,30}$",
                message="Имя пользователя должно содержать 3-30 символов (латиница, цифры и _.-)",
            )
        ],
        help_text="3-30 символов. Разрешены буквы, цифры, точки, дефисы и подчёркивания.",
    )
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    email_confirmed = models.BooleanField(default=False)
    organization = models.CharField(max_length=255, blank=True)
    time_zone = models.CharField(max_length=64, default="UTC")

    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.username


class EmailChangeRequest(models.Model):
    """Модель запроса на смену email с токеном подтверждения."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_requests")
    new_email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    confirmed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def is_expired(self) -> bool:
        """Проверяет, истек ли срок действия запроса на смену email."""
        return timezone.now() > self.expires_at


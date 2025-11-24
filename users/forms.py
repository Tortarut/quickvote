from django import forms
from django.contrib.auth import authenticate, password_validation
from django.utils.translation import gettext_lazy as _

from .models import User


class RegistrationForm(forms.ModelForm):
    """Форма регистрации нового пользователя с валидацией пароля."""
    password1 = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput,
        min_length=8,
    )
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("email", "username", "display_name")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Пользователь с таким email уже существует"))
        return email

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", _("Пароли не совпадают"))
        if password1:
            password_validation.validate_password(password1)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Форма входа. Поддерживает вход по email или username."""
    identifier = forms.CharField(label=_("Email или имя пользователя"))
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, initial=False)

    def clean(self):
        cleaned = super().clean()
        identifier = cleaned.get("identifier")
        password = cleaned.get("password")
        if identifier and password:
            user = authenticate(username=identifier, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email__iexact=identifier)
                except User.DoesNotExist:
                    user_obj = None
                if user_obj:
                    user = authenticate(username=user_obj.username, password=password)
            if not user:
                raise forms.ValidationError(_("Неверные учетные данные"))
            cleaned["user"] = user
        return cleaned


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя."""
    class Meta:
        model = User
        fields = (
            "display_name",
            "email",
            "organization",
            "bio",
            "time_zone",
            "avatar",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError(_("Email уже используется"))
        return email


class EmailChangeForm(forms.Form):
    """Форма запроса на смену email."""
    new_email = forms.EmailField()

    def clean_new_email(self):
        email = self.cleaned_data["new_email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email уже используется"))
        return email


class PasswordUpdateForm(forms.Form):
    """Форма смены пароля с проверкой текущего пароля."""
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data["current_password"]
        if not self.user.check_password(current):
            raise forms.ValidationError(_("Текущий пароль неверный"))
        return current

    def clean(self):
        cleaned = super().clean()
        new_password = cleaned.get("new_password")
        confirm_password = cleaned.get("confirm_password")
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("confirm_password", _("Пароли не совпадают"))
        if new_password:
            password_validation.validate_password(new_password, self.user)
        return cleaned


from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from .models import User, EmailChangeRequest


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для API."""
    class Meta:
        model = User
        fields = ("id", "username", "email", "display_name", "organization", "bio", "time_zone", "date_joined")
        read_only_fields = ("id", "date_joined")


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации с проверкой совпадения паролей."""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "username", "display_name", "password", "confirm_password")

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают"})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Сериализатор входа. Поддерживает вход по email или username."""
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")
        user = authenticate(username=identifier, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                user_obj = None
            if user_obj:
                user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError("Неверные учетные данные")
        attrs["user"] = user
        return attrs


class EmailChangeRequestSerializer(serializers.ModelSerializer):
    """Сериализатор запроса на смену email."""
    class Meta:
        model = EmailChangeRequest
        fields = ("id", "new_email", "created_at", "expires_at", "confirmed")
        read_only_fields = ("id", "created_at", "expires_at", "confirmed")


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, EmailChangeRequest


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Дополнительно",
            {
                "fields": (
                    "display_name",
                    "avatar",
                    "bio",
                    "email_confirmed",
                    "organization",
                    "time_zone",
                )
            },
        ),
    )
    list_display = ("username", "email", "email_confirmed", "is_staff", "date_joined")
    search_fields = ("username", "email")


@admin.register(EmailChangeRequest)
class EmailChangeRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "new_email", "confirmed", "created_at", "expires_at")
    search_fields = ("user__username", "new_email")
    list_filter = ("confirmed",)

from django.contrib import admin

from .models import NotificationRule, Notification, Complaint


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ("survey", "threshold", "email", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("rule", "sent_at", "total_responses")


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("survey", "reporter", "resolved", "created_at")
    list_filter = ("resolved",)

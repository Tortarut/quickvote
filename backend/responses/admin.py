from django.contrib import admin

from .models import SurveyResponse, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ("survey", "user", "is_anonymous", "submitted_at", "ip_address")
    list_filter = ("survey", "is_anonymous")
    search_fields = ("survey__title", "user__username", "ip_address")
    inlines = [AnswerInline]

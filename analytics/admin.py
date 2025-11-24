from django.contrib import admin

from .models import SurveyAnalyticsSnapshot, QuestionCorrelation


@admin.register(SurveyAnalyticsSnapshot)
class SurveyAnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ("survey", "total_participants", "completion_rate", "created_at")


@admin.register(QuestionCorrelation)
class QuestionCorrelationAdmin(admin.ModelAdmin):
    list_display = ("survey", "question_a", "question_b", "correlation_value", "created_at")

from django.contrib import admin

from .models import Survey, Question, Choice, SurveyTemplate


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "survey_type", "status", "created_at", "ends_at")
    list_filter = ("survey_type", "status")
    search_fields = ("title", "description", "author__username")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "survey", "question_type", "order")
    list_filter = ("question_type", "survey__survey_type")
    search_fields = ("text", "survey__title")
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("label", "question", "order")
    search_fields = ("label", "question__text")


@admin.register(SurveyTemplate)
class SurveyTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "category")
    list_filter = ("category",)

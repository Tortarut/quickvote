import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class Survey(models.Model):
    """Модель опроса. Хранит основную информацию об опросе и его настройки."""
    TYPE_ANONYMOUS = "anonymous"
    TYPE_PUBLIC = "public"
    TYPE_CHOICES = [
        (TYPE_ANONYMOUS, "Анонимный"),
        (TYPE_PUBLIC, "Публичный"),
    ]
    STATUS_ACTIVE = "active"
    STATUS_DRAFT = "draft"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Черновик"),
        (STATUS_ACTIVE, "Активный"),
        (STATUS_CLOSED, "Закрыт"),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="surveys")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, max_length=1000)
    survey_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_ANONYMOUS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    slug = models.SlugField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    is_template_based = models.BooleanField(default=False)
    theme = models.CharField(max_length=50, default="light")
    logo = models.ImageField(upload_to="survey_logos/", null=True, blank=True)
    welcome_message = models.CharField(max_length=255, blank=True)
    thank_you_message = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_editable(self):
        """Проверяет, можно ли редактировать опрос (не должно быть ответов)."""
        from responses.models import SurveyResponse

        return not SurveyResponse.objects.filter(survey=self).exists()

    @property
    def is_active(self):
        """Проверяет, активен ли опрос (статус активный и не истек срок)."""
        if self.status != self.STATUS_ACTIVE:
            return False
        if self.ends_at and timezone.now() > self.ends_at:
            return False
        return True


class Question(models.Model):
    """Модель вопроса в опросе. Поддерживает разные типы вопросов."""
    TYPE_SINGLE = "single"
    TYPE_MULTIPLE = "multiple"
    TYPE_TEXT = "text"
    TYPE_RATING = "rating"
    QUESTION_TYPES = [
        (TYPE_SINGLE, "Один вариант"),
        (TYPE_MULTIPLE, "Несколько вариантов"),
        (TYPE_TEXT, "Текст"),
        (TYPE_RATING, "Рейтинг 1-5"),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    max_text_length = models.PositiveIntegerField(default=1000)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.survey.title} - {self.text[:50]}"


class Choice(models.Model):
    """Модель варианта ответа для вопросов типа single/multiple."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    label = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label


class SurveyTemplate(models.Model):
    """Модель шаблона опроса для быстрого создания опросов по готовым сценариям."""
    CATEGORY_CHOICES = [
        ("satisfaction", "Оценка удовлетворенности"),
        ("marketing", "Маркетинговое исследование"),
        ("education", "Образовательный тест"),
        ("feedback", "Обратная связь о мероприятии"),
    ]
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

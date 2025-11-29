from rest_framework import serializers
from django.utils import timezone

from .models import Survey, Question, Choice, SurveyTemplate


class ChoiceSerializer(serializers.ModelSerializer):
    """Сериализатор варианта ответа."""
    class Meta:
        model = Choice
        fields = ("id", "label", "order")
        read_only_fields = ("id",)


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализатор вопроса с вложенными вариантами ответов."""
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ("id", "text", "question_type", "is_required", "order", "max_text_length", "choices")
        read_only_fields = ("id",)

    def validate(self, attrs):
        # Validation for choices is done in parent SurveySerializer.validate_questions
        # to avoid issues with initial_data not being available in nested serializers
        return attrs


class SurveySerializer(serializers.ModelSerializer):
    """Сериализатор опроса с вложенными вопросами. Ограничивает редактирование при наличии ответов."""
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Survey
        fields = (
            "id",
            "slug",
            "title",
            "description",
            "survey_type",
            "status",
            "created_at",
            "updated_at",
            "ends_at",
            "theme",
            "welcome_message",
            "thank_you_message",
            "questions",
        )
        read_only_fields = ("id", "slug", "status", "created_at", "updated_at")

    def validate_questions(self, value):
        if not value:
            raise serializers.ValidationError("Минимум один вопрос обязателен")
        # Validate that questions with choices have at least one choice
        # This validation happens before to_internal_value, so we get raw data
        for idx, question_data in enumerate(value):
            q_type = question_data.get("question_type")
            # Check if this is an existing question (has id) or new one
            question_id = question_data.get("id")
            choices = question_data.get("choices", [])
            if q_type in {Question.TYPE_SINGLE, Question.TYPE_MULTIPLE}:
                # For new questions (no id), choices are required
                if not question_id and not choices:
                    question_text = question_data.get("text", f"Вопрос {idx + 1}")
                    raise serializers.ValidationError(
                        f"Вопрос '{question_text}' с вариантами должен содержать хотя бы один вариант"
                    )
        return value

    def validate(self, attrs):
        ends_at = attrs.get("ends_at")
        if ends_at and ends_at <= timezone.now():
            raise serializers.ValidationError({"ends_at": "Дата окончания должна быть в будущем"})
        return attrs

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")
        # Author is set via perform_create in the viewset
        author = validated_data.pop("author", None) or self.context["request"].user
        survey = Survey.objects.create(author=author, **validated_data)
        self._save_questions(survey, questions_data)
        return survey

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", None)
        editable_fields = {"description", "ends_at", "status"}
        if not instance.is_editable:
            # only limited fields allowed
            for field in list(validated_data.keys()):
                if field not in editable_fields:
                    validated_data.pop(field, None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if questions_data and instance.is_editable:
            instance.questions.all().delete()
            self._save_questions(instance, questions_data)
        return instance

    def _save_questions(self, survey, questions_data):
        """Сохраняет вопросы и варианты ответов для опроса."""
        for index, question in enumerate(questions_data):
            choices_data = question.pop("choices", [])
            # Remove order from question dict if present, we set it explicitly
            question.pop("order", None)
            q = Question.objects.create(survey=survey, order=index, **question)
            for position, choice in enumerate(choices_data):
                # Remove order from choice dict if present, we set it explicitly
                choice.pop("order", None)
                Choice.objects.create(question=q, order=position, **choice)


class SurveyPublicSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного отображения опроса (без служебных полей)."""
    questions = QuestionSerializer(many=True)
    participants_count = serializers.IntegerField(source="responses.count", read_only=True)

    class Meta:
        model = Survey
        fields = (
            "slug",
            "title",
            "description",
            "survey_type",
            "ends_at",
            "participants_count",
            "welcome_message",
            "thank_you_message",
            "theme",
            "logo",
            "questions",
        )


class SurveyTemplateSerializer(serializers.ModelSerializer):
    """Сериализатор шаблона опроса."""
    class Meta:
        model = SurveyTemplate
        fields = ("id", "title", "category", "description", "payload")


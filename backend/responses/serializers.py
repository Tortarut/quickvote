from rest_framework import serializers

from surveys.models import Question, Choice, Survey
from .models import SurveyResponse, Answer


class AnswerSerializer(serializers.Serializer):
    """Сериализатор ответа на вопрос с валидацией в зависимости от типа вопроса."""
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    selected_choices = serializers.ListField(child=serializers.IntegerField(), required=False)
    text_answer = serializers.CharField(required=False, allow_blank=True)
    rating_value = serializers.IntegerField(required=False)

    def validate(self, attrs):
        question: Question = attrs["question"]
        q_type = question.question_type
        selected = attrs.get("selected_choices")
        text_answer = attrs.get("text_answer", "")
        rating_value = attrs.get("rating_value")

        if question.is_required:
            if q_type in {Question.TYPE_SINGLE, Question.TYPE_MULTIPLE} and not selected:
                raise serializers.ValidationError("Нужно выбрать хотя бы один вариант")
            if q_type == Question.TYPE_TEXT and not text_answer.strip():
                raise serializers.ValidationError("Ответ обязателен")
            if q_type == Question.TYPE_RATING and rating_value is None:
                raise serializers.ValidationError("Не выбран рейтинг")

        if q_type == Question.TYPE_TEXT and text_answer and len(text_answer) > question.max_text_length:
            raise serializers.ValidationError("Ответ превышает допустимую длину")

        if q_type == Question.TYPE_RATING and rating_value is not None:
            if rating_value < 1 or rating_value > 5:
                raise serializers.ValidationError("Рейтинг должен быть от 1 до 5")

        if selected:
            available_ids = question.choices.values_list("id", flat=True)
            invalid = set(selected) - set(available_ids)
            if invalid:
                raise serializers.ValidationError("Выбран недопустимый вариант")
            if q_type == Question.TYPE_SINGLE and len(selected) != 1:
                raise serializers.ValidationError("Нужно выбрать ровно один вариант")
        return attrs


class SurveyResponseSerializer(serializers.Serializer):
    """Сериализатор ответа на опрос. Проверяет, что все обязательные вопросы заполнены."""
    answers = AnswerSerializer(many=True)
    duration_seconds = serializers.IntegerField(required=False, min_value=0)

    def validate(self, attrs):
        survey: Survey = self.context["survey"]
        answers = attrs["answers"]
        question_ids = {answer["question"].id for answer in answers}
        for answer in answers:
            if answer["question"].survey_id != survey.id:
                raise serializers.ValidationError("Некорректный вопрос")
        missing_required = survey.questions.filter(is_required=True).exclude(id__in=question_ids)
        if missing_required.exists():
            raise serializers.ValidationError("Заполнены не все обязательные вопросы")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        survey = self.context["survey"]
        answers_data = validated_data["answers"]
        response = SurveyResponse.objects.create(
            survey=survey,
            user=request.user if request.user.is_authenticated else None,
            is_anonymous=survey.survey_type == Survey.TYPE_ANONYMOUS or not request.user.is_authenticated,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            duration_seconds=validated_data.get("duration_seconds") or 0,
        )
        for answer in answers_data:
            selected_choice_ids = answer.pop("selected_choices", [])
            answer_obj = Answer.objects.create(response=response, **answer)
            if selected_choice_ids:
                choices = Choice.objects.filter(id__in=selected_choice_ids)
                answer_obj.selected_choices.set(choices)
        return response


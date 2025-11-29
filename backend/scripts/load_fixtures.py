"""
Скрипт для загрузки тестовых данных из JSON фикстур в базу данных.
Создает пользователей, опросы с вопросами и ответы на опросы.
Пропускает уже существующих пользователей и дубликаты ответов.
"""
import os
import sys
import json
import django
from datetime import datetime

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from surveys.models import Survey, Question, Choice
from responses.models import SurveyResponse, Answer

User = get_user_model()


def load_users(users_data):
    """Загружает пользователей в базу данных. Пропускает уже существующих."""
    print("Загрузка пользователей...")
    user_map = {}
    
    for user_data in users_data:
        username = user_data["username"]
        
        # Проверяем, существует ли пользователь
        if User.objects.filter(username=username).exists():
            print(f"  ⚠ Пользователь {username} уже существует, пропускаем")
            user = User.objects.get(username=username)
        else:
            user = User.objects.create_user(
                username=username,
                email=user_data["email"],
                password=user_data["password"],
                display_name=user_data.get("display_name", ""),
                bio=user_data.get("bio", ""),
                organization=user_data.get("organization", ""),
                email_confirmed=user_data.get("email_confirmed", False),
            )
            print(f"  ✓ Создан пользователь: {username}")
        
        user_map[username] = user
    
    return user_map


def load_surveys(surveys_data, user_map):
    """Загружает опросы с вопросами и вариантами ответов в базу данных."""
    print("\nЗагрузка опросов...")
    survey_map = {}
    
    for survey_data in surveys_data:
        author_username = survey_data["author_username"]
        author = user_map.get(author_username)
        
        if not author:
            print(f"  ⚠ Автор {author_username} не найден, пропускаем опрос")
            continue
        
        # Создаем опрос
        ends_at = None
        if survey_data.get("ends_at"):
            ends_at = timezone.make_aware(datetime.fromisoformat(survey_data["ends_at"]))
        
        survey = Survey.objects.create(
            author=author,
            title=survey_data["title"],
            description=survey_data.get("description", ""),
            survey_type=survey_data["survey_type"],
            status=survey_data["status"],
            ends_at=ends_at,
            welcome_message=survey_data.get("welcome_message", ""),
            thank_you_message=survey_data.get("thank_you_message", ""),
        )
        
        survey_map[survey_data["id"]] = survey
        
        # Создаем вопросы
        for question_data in survey_data.get("questions", []):
            question = Question.objects.create(
                survey=survey,
                text=question_data["text"],
                question_type=question_data["question_type"],
                is_required=question_data.get("is_required", True),
                order=question_data.get("order", 0),
                max_text_length=question_data.get("max_text_length", 1000),
            )
            
            # Создаем варианты ответов
            for choice_data in question_data.get("choices", []):
                Choice.objects.create(
                    question=question,
                    label=choice_data["label"],
                    order=choice_data.get("order", 0),
                )
        
        num_questions = len(survey_data.get("questions", []))
        print(f"  ✓ Создан опрос: {survey.title} (вопросов: {num_questions})")
    
    return survey_map


def load_responses(responses_data, survey_map, user_map):
    """Загружает ответы на опросы. Пропускает дубликаты от одного пользователя."""
    print("\nЗагрузка ответов...")
    
    for response_data in responses_data:
        survey_id = response_data["survey_id"]
        survey = survey_map.get(survey_id)
        
        if not survey:
            print(f"  ⚠ Опрос с ID {survey_id} не найден, пропускаем ответ")
            continue
        
        # Получаем пользователя
        user = None
        if response_data.get("user_username"):
            user = user_map.get(response_data["user_username"])
        
        # Пропускаем дубликаты: один пользователь может ответить на опрос только один раз
        if user and SurveyResponse.objects.filter(survey=survey, user=user).exists():
            print(f"  ⚠ Ответ от пользователя {user.username} на опрос {survey.title} уже существует, пропускаем")
            continue
        
        # Создаем ответ
        submitted_at = timezone.now()
        if response_data.get("submitted_at"):
            submitted_at = timezone.make_aware(datetime.fromisoformat(response_data["submitted_at"]))
        
        response = SurveyResponse.objects.create(
            survey=survey,
            user=user,
            is_anonymous=response_data.get("is_anonymous", True),
            submitted_at=submitted_at,
            duration_seconds=response_data.get("duration_seconds", 0),
        )
        
        # Создаем ответы на вопросы
        answers_created = 0
        for answer_data in response_data.get("answers", []):
            question_order = answer_data["question_order"]
            
            # Находим вопрос
            question = Question.objects.filter(
                survey=survey,
                order=question_order
            ).first()
            
            if not question:
                continue
            
            # Создаем ответ
            answer = Answer.objects.create(
                response=response,
                question=question,
                text_answer=answer_data.get("text_answer", ""),
                rating_value=answer_data.get("rating_value"),
            )
            
            # Добавляем выбранные варианты
            if answer_data.get("selected_choice_order") is not None:
                choice_order = answer_data["selected_choice_order"]
                choice = question.choices.filter(order=choice_order).first()
                if choice:
                    answer.selected_choices.add(choice)
            
            elif answer_data.get("selected_choice_orders"):
                for choice_order in answer_data["selected_choice_orders"]:
                    choice = question.choices.filter(order=choice_order).first()
                    if choice:
                        answer.selected_choices.add(choice)
            
            answers_created += 1
        
        if answers_created > 0:
            print(f"  ✓ Создан ответ на опрос: {survey.title} ({answers_created} ответов на вопросы)")
    
    print(f"\n✓ Всего загружено ответов: {SurveyResponse.objects.count()}")


def main():
    """Основная функция: загружает все данные из JSON файла в базу данных."""
    fixtures_file = "fixtures/test_data.json"
    
    if not os.path.exists(fixtures_file):
        print(f"❌ Файл {fixtures_file} не найден!")
        print("Сначала запустите: python scripts/generate_fixtures.py")
        return
    
    print("Загрузка тестовых данных из фикстур...\n")
    
    with open(fixtures_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Загружаем данные
    user_map = load_users(data["users"])
    survey_map = load_surveys(data["surveys"], user_map)
    load_responses(data["responses"], survey_map, user_map)
    
    print("\n✓ Загрузка завершена успешно!")
    print(f"\nСтатистика:")
    print(f"  - Пользователей: {User.objects.count()}")
    print(f"  - Опросов: {Survey.objects.count()}")
    print(f"  - Ответов: {SurveyResponse.objects.count()}")


if __name__ == "__main__":
    main()


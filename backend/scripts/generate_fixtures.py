"""
Скрипт для генерации тестовых данных (фикстур) в JSON формате.
Создает пользователей, опросы с вопросами и ответы на опросы.
"""
import json
import random
from datetime import datetime, timedelta
from uuid import uuid4

# Данные для генерации
SURVEY_TITLES = [
    "Оценка удовлетворенности клиентов",
    "Маркетинговое исследование предпочтений",
    "Обратная связь о продукте",
    "Опрос о качестве обслуживания",
    "Исследование пользовательского опыта",
    "Оценка эффективности обучения",
    "Опрос о предпочтениях в еде",
    "Исследование мнений о бренде",
    "Обратная связь о мероприятии",
    "Опрос о здоровом образе жизни",
    "Исследование транспортных предпочтений",
    "Оценка качества работы команды",
    "Опрос о технологических предпочтениях",
    "Исследование покупательского поведения",
    "Обратная связь о сервисе",
]

SURVEY_DESCRIPTIONS = [
    "Помогите нам улучшить качество обслуживания",
    "Ваше мнение очень важно для нас",
    "Заполните опрос, это займет всего 2 минуты",
    "Мы ценим ваше время и мнение",
    "Поделитесь своими мыслями",
    "Ваши ответы помогут нам стать лучше",
    "Примите участие в исследовании",
    "Расскажите нам о своем опыте",
]

QUESTION_TEXTS = {
    "single": [
        "Как вы оцениваете качество обслуживания?",
        "Какой вариант вам больше всего подходит?",
        "Выберите наиболее подходящий вариант",
        "Какой из вариантов вы предпочитаете?",
        "Что для вас наиболее важно?",
    ],
    "multiple": [
        "Какие функции вам наиболее важны? (можно выбрать несколько)",
        "Отметьте все подходящие варианты",
        "Что вас интересует? (выберите все подходящее)",
        "Какие характеристики важны для вас?",
        "Выберите все применимые варианты",
    ],
    "text": [
        "Оставьте ваш отзыв",
        "Поделитесь своими мыслями",
        "Что вы думаете об этом?",
        "Напишите ваше мнение",
        "Дополнительные комментарии",
    ],
    "rating": [
        "Оцените по шкале от 1 до 5",
        "Как вы оцениваете это?",
        "Поставьте оценку от 1 до 5",
        "Оцените качество",
        "Какова ваша оценка?",
    ],
}

CHOICE_LABELS = {
    "single": [
        ["Отлично", "Хорошо", "Удовлетворительно", "Плохо"],
        ["Да", "Нет", "Не знаю"],
        ["Вариант 1", "Вариант 2", "Вариант 3", "Вариант 4"],
        ["Полностью согласен", "Согласен", "Не согласен", "Полностью не согласен"],
        ["Всегда", "Часто", "Иногда", "Никогда"],
    ],
    "multiple": [
        ["Функция 1", "Функция 2", "Функция 3", "Функция 4"],
        ["Вариант A", "Вариант B", "Вариант C", "Вариант D"],
        ["Характеристика 1", "Характеристика 2", "Характеристика 3"],
        ["Опция 1", "Опция 2", "Опция 3", "Опция 4", "Опция 5"],
    ],
}

USERNAMES = [
    "demo_user", "john_doe", "jane_smith", "alex_petrov", "maria_ivanova",
    "test_user", "admin_demo", "survey_master", "research_pro", "data_analyst",
    "marketing_guru", "feedback_collector", "poll_creator", "user_researcher",
]

def generate_users():
    """Генерирует список тестовых пользователей с базовыми данными."""
    users = []
    for i, username in enumerate(USERNAMES):
        user = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "TestPass123!",  # Общий пароль для всех тестовых пользователей
            "display_name": username.replace("_", " ").title(),
            "bio": f"Тестовый пользователь {i+1}",
            "organization": random.choice(["Компания А", "Компания Б", "Организация В", "Компания Г", ""]),
            "email_confirmed": True,
        }
        users.append(user)
    return users


def generate_surveys(users):
    """
    Генерирует опросы для пользователей.
    Первый пользователь (demo_user) получает 10 опросов, остальные - по 1-3.
    """
    surveys = []
    survey_id = 1
    
    # Первый пользователь (demo_user) получает 10 опросов
    main_user = users[0]
    for i in range(10):
        survey = generate_single_survey(survey_id, main_user, i)
        surveys.append(survey)
        survey_id += 1
    
    # Остальные пользователи получают по 1-3 опроса
    for user in users[1:]:
        num_surveys = random.randint(1, 3)
        for i in range(num_surveys):
            survey = generate_single_survey(survey_id, user, i)
            surveys.append(survey)
            survey_id += 1
    
    return surveys


def generate_single_survey(survey_id, user, index):
    """Генерирует один опрос со случайными параметрами и вопросами."""
    status = random.choice(["active", "active", "active", "draft", "closed"])
    survey_type = random.choice(["anonymous", "public"])
    
    # Для некоторых опросов добавляем дату окончания
    ends_at = None
    if random.random() > 0.5:
        days_ahead = random.randint(1, 30)
        ends_at = (datetime.now() + timedelta(days=days_ahead)).isoformat()
    
    survey = {
        "id": survey_id,
        "author_username": user["username"],
        "title": random.choice(SURVEY_TITLES) + (f" #{index+1}" if index > 0 else ""),
        "description": random.choice(SURVEY_DESCRIPTIONS),
        "survey_type": survey_type,
        "status": status,
        "ends_at": ends_at,
        "welcome_message": random.choice(["Добро пожаловать!", "Спасибо за участие!", ""]),
        "thank_you_message": random.choice(["Спасибо за ваш ответ!", "Ваше мнение важно для нас!", ""]),
        "questions": [],
    }
    
    # Генерируем вопросы
    num_questions = random.randint(3, 6)
    question_types = ["single", "multiple", "text", "rating"]
    
    for q_order in range(num_questions):
        question_type = random.choice(question_types)
        question = generate_question(q_order, question_type)
        survey["questions"].append(question)
    
    return survey


def generate_question(order, question_type):
    """Генерирует один вопрос указанного типа с вариантами ответов (если требуется)."""
    question = {
        "order": order,
        "text": random.choice(QUESTION_TEXTS[question_type]),
        "question_type": question_type,
        "is_required": random.choice([True, True, True, False]),  # Чаще обязательные
        "max_text_length": 1000,
        "choices": [],
    }
    
    # Добавляем варианты ответов для single и multiple
    if question_type in ["single", "multiple"]:
        choice_set = random.choice(CHOICE_LABELS[question_type])
        for c_order, label in enumerate(choice_set):
            question["choices"].append({
                "order": c_order,
                "label": label,
            })
    
    return question


def generate_responses(surveys, users):
    """
    Генерирует ответы на опросы.
    Гарантирует, что каждый авторизованный пользователь отвечает на опрос только один раз.
    Для анонимных опросов допускается несколько анонимных ответов.
    """
    responses = []
    response_id = 1
    
    for survey in surveys:
        # Пропускаем черновики
        if survey["status"] == "draft":
            continue
        
        answered_users = set()  # Отслеживание авторизованных пользователей, уже ответивших
        anonymous_count = 0
        
        num_responses = random.randint(5, 20)
        
        # Для публичных опросов - только авторизованные пользователи
        # Для анонимных - авторизованные + ограниченное количество анонимных
        if survey["survey_type"] == "public":
            available_users = users
            max_anonymous = 0
        else:
            available_users = users
            max_anonymous = random.randint(3, 8)
        
        attempts = 0
        max_attempts = num_responses * 5  # Ограничение попыток
        
        survey_responses = [r for r in responses if r["survey_id"] == survey["id"]]
        
        while len(survey_responses) < num_responses and attempts < max_attempts:
            attempts += 1
            
            # Решение: создать анонимный ответ или от пользователя
            use_anonymous = (
                survey["survey_type"] == "anonymous" and 
                anonymous_count < max_anonymous and
                random.random() < 0.3
            )
            
            if use_anonymous:
                user = None
                user_username = None
                anonymous_count += 1
            else:
                # Выбираем случайного пользователя из доступных
                if not available_users:
                    break
                
                # Выбираем только из пользователей, которые еще не ответили
                available = [u for u in available_users if u["username"] not in answered_users]
                if not available:
                    # Если все пользователи ответили, добавляем анонимные (если возможно)
                    if anonymous_count < max_anonymous:
                        user = None
                        user_username = None
                        anonymous_count += 1
                    else:
                        break
                else:
                    user = random.choice(available)
                    user_username = user["username"]
                    answered_users.add(user_username)
            
            response = {
                "id": response_id,
                "survey_id": survey["id"],
                "user_username": user_username,
                "is_anonymous": survey["survey_type"] == "anonymous" or user is None,
                "submitted_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                "duration_seconds": random.randint(30, 300),
                "answers": [],
            }
            
            # Генерируем ответы на вопросы
            for question in survey["questions"]:
                answer = generate_answer(question)
                response["answers"].append(answer)
            
            responses.append(response)
            survey_responses.append(response)
            response_id += 1
    
    return responses


def generate_answer(question):
    """Генерирует ответ на вопрос в зависимости от типа вопроса."""
    answer = {
        "question_order": question["order"],
        "question_type": question["question_type"],
    }
    
    if question["question_type"] == "single":
        # Выбираем один вариант
        if question["choices"]:
            answer["selected_choice_order"] = random.randint(0, len(question["choices"]) - 1)
    
    elif question["question_type"] == "multiple":
        # Выбираем 1-3 варианта
        if question["choices"]:
            num_choices = random.randint(1, min(3, len(question["choices"])))
            selected = random.sample(range(len(question["choices"])), num_choices)
            answer["selected_choice_orders"] = selected
    
    elif question["question_type"] == "text":
        # Генерируем текстовый ответ
        text_responses = [
            "Отличный сервис, все понравилось!",
            "Хорошо, но есть что улучшить",
            "Нормально, без особых замечаний",
            "Не очень доволен",
            "Все отлично, рекомендую!",
            "Хорошее качество",
            "Удовлетворительно",
        ]
        answer["text_answer"] = random.choice(text_responses)
    
    elif question["question_type"] == "rating":
        # Генерируем оценку от 1 до 5
        answer["rating_value"] = random.randint(1, 5)
    
    return answer


def main():
    """Основная функция: генерирует все данные и сохраняет в JSON файл."""
    print("Генерация тестовых данных...")
    
    # Генерируем данные
    users = generate_users()
    surveys = generate_surveys(users)
    responses = generate_responses(surveys, users)
    
    # Сохраняем в JSON файлы
    output = {
        "users": users,
        "surveys": surveys,
        "responses": responses,
    }
    
    with open("fixtures/test_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Сгенерировано:")
    print(f"  - Пользователей: {len(users)}")
    print(f"  - Опросов: {len(surveys)}")
    print(f"  - Ответов: {len(responses)}")
    print(f"✓ Данные сохранены в fixtures/test_data.json")


if __name__ == "__main__":
    main()


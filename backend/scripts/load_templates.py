"""
Скрипт для загрузки шаблонов опросов в базу данных.
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from surveys.models import SurveyTemplate

templates = [
    {
        "title": "Оценка удовлетворенности",
        "category": "satisfaction",
        "description": "Измерьте NPS и удовлетворенность сервисом",
        "payload": {
            "survey_type": "public",
            "questions": [
                {
                    "text": "Насколько вы довольны продуктом?",
                    "question_type": "rating",
                    "is_required": True,
                },
                {
                    "text": "Что можно улучшить?",
                    "question_type": "text",
                    "is_required": False,
                },
            ],
        },
    },
    {
        "title": "Маркетинговое исследование",
        "category": "marketing",
        "description": "Поймите предпочтения клиентов",
        "payload": {
            "survey_type": "anonymous",
            "questions": [
                {
                    "text": "Какой канал привлечения вы предпочитаете?",
                    "question_type": "multiple",
                    "is_required": True,
                    "choices": [
                        {"label": "Соцсети"},
                        {"label": "Email"},
                        {"label": "Web"},
                    ],
                },
                {
                    "text": "Как часто вы покупаете?",
                    "question_type": "single",
                    "is_required": True,
                    "choices": [
                        {"label": "Каждую неделю"},
                        {"label": "Раз в месяц"},
                        {"label": "Реже"},
                    ],
                },
            ],
        },
    },
    {
        "title": "Образовательный тест",
        "category": "education",
        "description": "Быстрая проверка знаний",
        "payload": {
            "survey_type": "public",
            "questions": [
                {
                    "text": "Что такое REST?",
                    "question_type": "text",
                    "is_required": True,
                },
                {
                    "text": "Выберите верные утверждения",
                    "question_type": "multiple",
                    "is_required": True,
                    "choices": [
                        {"label": "REST основан на HTTP"},
                        {"label": "REST требует SOAP"},
                        {"label": "REST подразумевает stateless"},
                    ],
                },
            ],
        },
    },
    {
        "title": "Обратная связь о мероприятии",
        "category": "feedback",
        "description": "Соберите отзывы посетителей",
        "payload": {
            "survey_type": "anonymous",
            "questions": [
                {
                    "text": "Оцените мероприятие",
                    "question_type": "rating",
                    "is_required": True,
                },
                {
                    "text": "Что понравилось больше всего?",
                    "question_type": "text",
                    "is_required": False,
                },
            ],
        },
    },
]

def main():
    """Загружает шаблоны в базу данных."""
    print("Загрузка шаблонов опросов...\n")
    
    for tpl in templates:
        template, created = SurveyTemplate.objects.update_or_create(
            title=tpl["title"],
            defaults={
                "category": tpl["category"],
                "description": tpl["description"],
                "payload": tpl["payload"],
            },
        )
        if created:
            print(f"✓ Создан шаблон: {tpl['title']}")
        else:
            print(f"✓ Обновлен шаблон: {tpl['title']}")
    
    print(f"\n✓ Загружено шаблонов: {SurveyTemplate.objects.count()}")


if __name__ == "__main__":
    main()


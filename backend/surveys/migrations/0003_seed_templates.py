from django.db import migrations


def seed_templates(apps, schema_editor):
    SurveyTemplate = apps.get_model("surveys", "SurveyTemplate")
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
    for tpl in templates:
        SurveyTemplate.objects.update_or_create(
            title=tpl["title"],
            defaults={
                "category": tpl["category"],
                "description": tpl["description"],
                "payload": tpl["payload"],
            },
        )


def remove_templates(apps, schema_editor):
    SurveyTemplate = apps.get_model("surveys", "SurveyTemplate")
    SurveyTemplate.objects.filter(
        title__in=[
            "Оценка удовлетворенности",
            "Маркетинговое исследование",
            "Образовательный тест",
            "Обратная связь о мероприятии",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(seed_templates, remove_templates),
    ]


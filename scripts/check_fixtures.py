"""Проверка структуры и статистики сгенерированных фикстур."""
import json

with open("fixtures/test_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"✓ Пользователей: {len(data['users'])}")
print(f"✓ Опросов: {len(data['surveys'])}")
print(f"✓ Ответов: {len(data['responses'])}")

# Проверяем demo_user
demo_surveys = [s for s in data['surveys'] if s['author_username'] == 'demo_user']
print(f"\n✓ Опросов у demo_user: {len(demo_surveys)}")

# Проверяем структуру первого опроса
if data['surveys']:
    first_survey = data['surveys'][0]
    print(f"\nПример опроса:")
    print(f"  Название: {first_survey['title']}")
    print(f"  Автор: {first_survey['author_username']}")
    print(f"  Тип: {first_survey['survey_type']}")
    print(f"  Статус: {first_survey['status']}")
    print(f"  Вопросов: {len(first_survey.get('questions', []))}")

# Проверяем ответы
if data['responses']:
    print(f"\nПример ответа:")
    first_response = data['responses'][0]
    print(f"  Опрос ID: {first_response['survey_id']}")
    print(f"  Пользователь: {first_response.get('user_username', 'Анонимный')}")
    print(f"  Ответов на вопросы: {len(first_response.get('answers', []))}")


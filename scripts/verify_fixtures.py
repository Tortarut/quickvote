"""
Проверка фикстур на отсутствие дубликатов ответов.
Проверяет, что каждый авторизованный пользователь отвечает на опрос только один раз.
"""
import json

with open("fixtures/test_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Проверка фикстур на дубликаты ответов...\n")

# Отслеживание ответов: ключ (survey_id, user_username) -> количество
response_map = {}
duplicates = []

for response in data["responses"]:
    survey_id = response["survey_id"]
    user_username = response.get("user_username")
    
    key = (survey_id, user_username)
    
    if key in response_map:
        duplicates.append({
            "survey_id": survey_id,
            "user_username": user_username or "Анонимный",
            "count": response_map[key] + 1
        })
        response_map[key] += 1
    else:
        response_map[key] = 1

# Разделение дубликатов: авторизованные пользователи и анонимные
auth_duplicates = [d for d in duplicates if d["user_username"] != "Анонимный"]
anon_duplicates = [d for d in duplicates if d["user_username"] == "Анонимный"]

if auth_duplicates:
    print("❌ Найдены дубликаты ответов от авторизованных пользователей:")
    for dup in auth_duplicates:
        print(f"  - Опрос ID {dup['survey_id']}, пользователь: {dup['user_username']}, ответов: {dup['count']}")
    print(f"\nВсего дубликатов от авторизованных: {len(auth_duplicates)}")

if anon_duplicates:
    print(f"\n⚠ Найдены множественные анонимные ответы (это нормально для анонимных опросов):")
    print(f"  Всего случаев: {len(anon_duplicates)}")

if not auth_duplicates:
    print("✓ Дубликатов не найдено!")
    print(f"✓ Всего уникальных комбинаций (опрос, пользователь): {len(response_map)}")
    print(f"✓ Всего ответов: {len(data['responses'])}")
    
    # Статистика по опросам
    survey_responses = {}
    for response in data["responses"]:
        survey_id = response["survey_id"]
        survey_responses[survey_id] = survey_responses.get(survey_id, 0) + 1
    
    print(f"\nСтатистика по опросам:")
    print(f"  - Опросов с ответами: {len(survey_responses)}")
    print(f"  - Среднее ответов на опрос: {sum(survey_responses.values()) / len(survey_responses):.1f}")
    print(f"  - Минимум ответов: {min(survey_responses.values())}")
    print(f"  - Максимум ответов: {max(survey_responses.values())}")


"""
Скрипт для полной очистки базы данных от всех данных.
Удаляет опросы, ответы, пользователей (кроме суперпользователей и staff).
Выполняется без подтверждения.
"""
import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from surveys.models import Survey, Question, Choice, SurveyTemplate
from responses.models import SurveyResponse, Answer
from users.models import User, EmailChangeRequest
from notifications.models import Notification, NotificationRule

print("Очистка базы данных...\n")

# Удаление в правильном порядке: сначала зависимые объекты
print("Удаление ответов...")
Answer.objects.all().delete()
print(f"  ✓ Удалено ответов на вопросы: {Answer.objects.count()}")

print("Удаление ответов на опросы...")
SurveyResponse.objects.all().delete()
print(f"  ✓ Удалено ответов на опросы: {SurveyResponse.objects.count()}")

print("Удаление вариантов ответов...")
Choice.objects.all().delete()
print(f"  ✓ Удалено вариантов ответов: {Choice.objects.count()}")

print("Удаление вопросов...")
Question.objects.all().delete()
print(f"  ✓ Удалено вопросов: {Question.objects.count()}")

print("Удаление опросов...")
Survey.objects.all().delete()
print(f"  ✓ Удалено опросов: {Survey.objects.count()}")

print("Удаление шаблонов опросов...")
SurveyTemplate.objects.all().delete()
print(f"  ✓ Удалено шаблонов: {SurveyTemplate.objects.count()}")

print("Удаление уведомлений...")
Notification.objects.all().delete()
print(f"  ✓ Удалено уведомлений: {Notification.objects.count()}")

print("Удаление правил уведомлений...")
NotificationRule.objects.all().delete()
print(f"  ✓ Удалено правил уведомлений: {NotificationRule.objects.count()}")

print("Удаление запросов на смену email...")
EmailChangeRequest.objects.all().delete()
print(f"  ✓ Удалено запросов на смену email: {EmailChangeRequest.objects.count()}")

# Пользователей удаляем в последнюю очередь (сохраняем суперпользователей и staff)
print("Удаление пользователей...")
User.objects.filter(is_superuser=False, is_staff=False).delete()
print(f"  ✓ Удалено обычных пользователей")
print(f"  ⚠ Суперпользователи и staff сохранены")

print("\n✓ База данных очищена!")
print(f"\nОсталось:")
print(f"  - Пользователей: {User.objects.count()}")
print(f"  - Опросов: {Survey.objects.count()}")
print(f"  - Ответов: {SurveyResponse.objects.count()}")


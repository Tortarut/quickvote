from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from surveys.models import Survey, Question, Choice
from .models import SurveyResponse, Answer
from .views import build_statistics_payload

User = get_user_model()


class SurveyResponseTest(TestCase):
    """Тесты для ответов на опросы."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client = APIClient()
        
        self.survey = Survey.objects.create(
            author=self.user,
            title="Test Survey",
            status=Survey.STATUS_ACTIVE,
            survey_type=Survey.TYPE_PUBLIC
        )
        
        # Создаем вопросы разных типов
        self.single_question = Question.objects.create(
            survey=self.survey,
            text="Single choice?",
            question_type=Question.TYPE_SINGLE,
            is_required=True
        )
        self.choice1 = Choice.objects.create(question=self.single_question, label="Option 1", order=0)
        self.choice2 = Choice.objects.create(question=self.single_question, label="Option 2", order=1)
        
        self.text_question = Question.objects.create(
            survey=self.survey,
            text="Text question?",
            question_type=Question.TYPE_TEXT,
            is_required=True
        )
        
        self.rating_question = Question.objects.create(
            survey=self.survey,
            text="Rating question?",
            question_type=Question.TYPE_RATING,
            is_required=True
        )
    
    def test_submit_response_with_all_question_types(self):
        """Тест: отправка ответа с вопросами всех типов."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            "answers": [
                {
                    "question": self.single_question.id,
                    "selected_choices": [self.choice1.id]
                },
                {
                    "question": self.text_question.id,
                    "text_answer": "Test text answer"
                },
                {
                    "question": self.rating_question.id,
                    "rating_value": 4
                }
            ],
            "duration_seconds": 120
        }
        
        response = self.client.post(
            f"/responses/api/{self.survey.slug}/submit/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SurveyResponse.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 3)
        
        survey_response = SurveyResponse.objects.first()
        self.assertEqual(survey_response.user, self.user)
        self.assertEqual(survey_response.duration_seconds, 120)
        self.assertFalse(survey_response.is_anonymous)
    
    def test_duplicate_response_prevention(self):
        """Тест: предотвращение дубликатов ответов от одного пользователя."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            "answers": [
                {
                    "question": self.single_question.id,
                    "selected_choices": [self.choice1.id]
                },
                {
                    "question": self.text_question.id,
                    "text_answer": "First answer"
                },
                {
                    "question": self.rating_question.id,
                    "rating_value": 5
                }
            ]
        }
        
        # Первый ответ
        response1 = self.client.post(
            f"/responses/api/{self.survey.slug}/submit/",
            data,
            format="json"
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Попытка второго ответа
        data["answers"][1]["text_answer"] = "Second answer"
        response2 = self.client.post(
            f"/responses/api/{self.survey.slug}/submit/",
            data,
            format="json"
        )
        
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("уже голосовали", response2.data["detail"])
        self.assertEqual(SurveyResponse.objects.count(), 1)
    
    def test_required_questions_validation(self):
        """Тест: валидация обязательных вопросов."""
        self.client.force_authenticate(user=self.user)
        
        # Отправляем ответ без обязательного вопроса
        data = {
            "answers": [
                {
                    "question": self.single_question.id,
                    "selected_choices": [self.choice1.id]
                }
                # Пропускаем text_question и rating_question (обязательные)
            ]
        }
        
        response = self.client.post(
            f"/responses/api/{self.survey.slug}/submit/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("обязательные", str(response.data))
    
    def test_anonymous_response(self):
        """Тест: анонимный ответ на анонимный опрос."""
        anonymous_survey = Survey.objects.create(
            author=self.user,
            title="Anonymous Survey",
            status=Survey.STATUS_ACTIVE,
            survey_type=Survey.TYPE_ANONYMOUS
        )
        
        question = Question.objects.create(
            survey=anonymous_survey,
            text="Question?",
            question_type=Question.TYPE_TEXT,
            is_required=True
        )
        
        # Не аутентифицированный пользователь
        self.client.force_authenticate(user=None)
        
        data = {
            "answers": [
                {
                    "question": question.id,
                    "text_answer": "Anonymous answer"
                }
            ]
        }
        
        response = self.client.post(
            f"/responses/api/{anonymous_survey.slug}/submit/",
            data,
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        survey_response = SurveyResponse.objects.first()
        self.assertIsNone(survey_response.user)
        self.assertTrue(survey_response.is_anonymous)
    
    def test_statistics_building(self):
        """Тест: построение статистики опроса."""
        # Создаем несколько ответов
        response1 = SurveyResponse.objects.create(
            survey=self.survey,
            user=self.user,
            is_anonymous=False
        )
        
        Answer.objects.create(
            response=response1,
            question=self.single_question
        ).selected_choices.add(self.choice1)
        
        Answer.objects.create(
            response=response1,
            question=self.text_question,
            text_answer="Answer 1"
        )
        
        Answer.objects.create(
            response=response1,
            question=self.rating_question,
            rating_value=5
        )
        
        # Второй ответ
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123"
        )
        response2 = SurveyResponse.objects.create(
            survey=self.survey,
            user=other_user,
            is_anonymous=False
        )
        
        Answer.objects.create(
            response=response2,
            question=self.single_question
        ).selected_choices.add(self.choice1)
        
        Answer.objects.create(
            response=response2,
            question=self.text_question,
            text_answer="Answer 2"
        )
        
        Answer.objects.create(
            response=response2,
            question=self.rating_question,
            rating_value=4
        )
        
        # Строим статистику
        stats = build_statistics_payload(self.survey)
        
        self.assertEqual(stats["total_responses"], 2)
        self.assertEqual(len(stats["questions"]), 3)
        
        # Проверяем статистику для single choice
        single_stats = next(q for q in stats["questions"] if q["type"] == Question.TYPE_SINGLE)
        self.assertEqual(len(single_stats["options"]), 1)
        self.assertEqual(single_stats["options"][0]["label"], "Option 1")
        self.assertEqual(single_stats["options"][0]["count"], 2)
        self.assertEqual(single_stats["options"][0]["percentage"], 100.0)
        
        # Проверяем статистику для text
        text_stats = next(q for q in stats["questions"] if q["type"] == Question.TYPE_TEXT)
        self.assertEqual(len(text_stats["responses"]), 2)
        self.assertIn("Answer 1", text_stats["responses"])
        self.assertIn("Answer 2", text_stats["responses"])
        
        # Проверяем статистику для rating
        rating_stats = next(q for q in stats["questions"] if q["type"] == Question.TYPE_RATING)
        self.assertEqual(rating_stats["average"], 4.5)  # (5 + 4) / 2
        self.assertEqual(len(rating_stats["distribution"]), 2)

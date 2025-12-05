from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from .models import Survey, Question, Choice, SurveyTemplate

User = get_user_model()


class SurveyModelTest(TestCase):
    """Тесты для модели Survey."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    def test_survey_is_editable_without_responses(self):
        """Тест: опрос можно редактировать, если нет ответов."""
        survey = Survey.objects.create(
            author=self.user,
            title="Test Survey",
            status=Survey.STATUS_ACTIVE
        )
        self.assertTrue(survey.is_editable)
    
    def test_survey_is_not_editable_with_responses(self):
        """Тест: опрос нельзя редактировать, если есть ответы."""
        from responses.models import SurveyResponse
        
        survey = Survey.objects.create(
            author=self.user,
            title="Test Survey",
            status=Survey.STATUS_ACTIVE
        )
        SurveyResponse.objects.create(survey=survey, is_anonymous=True)
        
        self.assertFalse(survey.is_editable)
    
    def test_survey_is_active(self):
        """Тест: опрос активен, если статус active и не истек срок."""
        future_date = timezone.now() + timedelta(days=1)
        survey = Survey.objects.create(
            author=self.user,
            title="Test Survey",
            status=Survey.STATUS_ACTIVE,
            ends_at=future_date
        )
        self.assertTrue(survey.is_active)
    
    def test_survey_is_not_active_when_closed(self):
        """Тест: закрытый опрос не активен."""
        survey = Survey.objects.create(
            author=self.user,
            title="Test Survey",
            status=Survey.STATUS_CLOSED
        )
        self.assertFalse(survey.is_active)
    
    def test_survey_is_not_active_when_expired(self):
        """Тест: опрос не активен, если истек срок."""
        past_date = timezone.now() - timedelta(days=1)
        survey = Survey.objects.create(
            author=self.user,
            title="Test Survey",
            status=Survey.STATUS_ACTIVE,
            ends_at=past_date
        )
        self.assertFalse(survey.is_active)


class SurveyAPITest(TestCase):
    """Тесты для API опросов."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_survey_with_questions(self):
        """Тест: создание опроса с вопросами разных типов через API."""
        data = {
            "title": "Test Survey",
            "description": "Test Description",
            "survey_type": Survey.TYPE_ANONYMOUS,
            "questions": [
                {
                    "text": "Single choice question?",
                    "question_type": Question.TYPE_SINGLE,
                    "is_required": True,
                    "choices": [
                        {"label": "Option 1", "order": 0},
                        {"label": "Option 2", "order": 1}
                    ]
                },
                {
                    "text": "Text question?",
                    "question_type": Question.TYPE_TEXT,
                    "is_required": False
                },
                {
                    "text": "Rating question?",
                    "question_type": Question.TYPE_RATING,
                    "is_required": True
                }
            ]
        }
        
        response = self.client.post("/api/surveys/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 3)
        
        survey = Survey.objects.first()
        self.assertEqual(survey.title, "Test Survey")
        self.assertEqual(survey.author, self.user)
        self.assertEqual(survey.questions.count(), 3)
    
    def test_author_can_update_survey(self):
        """Тест: автор может обновить свой опрос."""
        survey = Survey.objects.create(
            author=self.user,
            title="Original Title",
            status=Survey.STATUS_ACTIVE
        )
        
        data = {"title": "Updated Title", "description": "Updated"}
        response = self.client.patch(f"/api/surveys/{survey.slug}/", data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        survey.refresh_from_db()
        self.assertEqual(survey.title, "Updated Title")
    
    def test_non_author_cannot_update_survey(self):
        """Тест: не-автор не может обновить чужой опрос."""
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123"
        )
        survey = Survey.objects.create(
            author=other_user,
            title="Other User Survey",
            status=Survey.STATUS_ACTIVE
        )
        
        data = {"title": "Hacked Title"}
        response = self.client.patch(f"/api/surveys/{survey.slug}/", data, format="json")
        
        # get_queryset фильтрует опросы, поэтому опрос не будет найден (404)
        # или будет запрещен доступ (403) в зависимости от реализации
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_admin_can_update_any_survey(self):
        """Тест: администратор может обновить любой опрос."""
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123"
        )
        self.user.is_staff = True
        self.user.save()
        
        survey = Survey.objects.create(
            author=other_user,
            title="Other User Survey",
            status=Survey.STATUS_ACTIVE
        )
        
        data = {"title": "Admin Updated Title"}
        response = self.client.patch(f"/api/surveys/{survey.slug}/", data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        survey.refresh_from_db()
        self.assertEqual(survey.title, "Admin Updated Title")


class SurveyTemplateTest(TestCase):
    """Тесты для шаблонов опросов."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.template = SurveyTemplate.objects.create(
            title="Test Template",
            category="satisfaction",
            description="Test template description",
            payload={
                "title": "Template Survey",
                "description": "From template",
                "survey_type": Survey.TYPE_ANONYMOUS,
                "questions": [
                    {
                        "text": "Template question?",
                        "question_type": Question.TYPE_SINGLE,
                        "is_required": True,
                        "choices": [
                            {"label": "Yes", "order": 0},
                            {"label": "No", "order": 1}
                        ]
                    }
                ]
            }
        )
    
    def test_create_survey_from_template(self):
        """Тест: создание опроса из шаблона."""
        response = self.client.post(
            f"/api/templates/{self.template.id}/instantiate/",
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 1)
        
        survey = Survey.objects.first()
        self.assertEqual(survey.title, "Template Survey")
        self.assertTrue(survey.is_template_based)
        self.assertEqual(survey.questions.count(), 1)
        
        question = survey.questions.first()
        self.assertEqual(question.text, "Template question?")
        self.assertEqual(question.choices.count(), 2)

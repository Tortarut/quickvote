from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserRegistrationTest(TestCase):
    """Тесты для регистрации пользователей."""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_user_registration(self):
        """Тест: регистрация нового пользователя через API."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        
        response = self.client.post("/auth/api/register/", data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        
        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("TestPass123!"))
    
    def test_user_registration_validation(self):
        """Тест: валидация данных при регистрации."""
        # Неправильный username (слишком короткий)
        data = {
            "username": "ab",  # Меньше 3 символов
            "email": "test@example.com",
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        
        response = self.client.post("/auth/api/register/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Тест: вход пользователя в систему."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        data = {
            "identifier": "testuser",
            "password": "testpass123"
        }
        
        response = self.client.post("/auth/api/login/", data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["username"], "testuser")
    
    def test_user_profile_update(self):
        """Тест: обновление профиля пользователя."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        self.client.force_authenticate(user=user)
        
        data = {
            "display_name": "Test User",
            "bio": "Test bio",
            "organization": "Test Org"
        }
        
        response = self.client.patch("/auth/api/profile/", data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.display_name, "Test User")
        self.assertEqual(user.bio, "Test bio")
        self.assertEqual(user.organization, "Test Org")

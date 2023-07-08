from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class RegistrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.user = get_user_model().objects.create_user(
            username="firstuser",
            email="firstuser@email.com",
            password="secretpassword",
        )

    def test_user_registration(self):
        response = self.client.post(
            "/api/v1/dj-rest-auth/registration/",
            data={
                "username": "testuser",
                "email": "testuser@email.com",
                "password1": "secretpassword",
                "password2": "secretpassword",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            get_user_model().objects.filter(email="testuser@email.com").exists()
        )

    def test_user_registration_with_missing_fields(self):
        response = self.client.post("/api/v1/dj-rest-auth/registration/", data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("password1", response.data)
        self.assertIn("password2", response.data)

    def test_user_registration_with_invalid_email(self):
        response = self.client.post(
            "/api/v1/dj-rest-auth/registration/",
            data={
                "username": "testuser",
                "email": "testuser",
                "password1": "secretpassword",
                "password2": "secretpassword",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_registration_with_weak_password(self):
        response = self.client.post(
            "/api/v1/dj-rest-auth/registration/",
            data={
                "username": "testuser",
                "email": "testuser@email.com",
                "password1": "12345",
                "password2": "12345",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password1", response.data)

    def test_user_registration_with_duplicate_email(self):
        response = self.client.post(
            "/api/v1/dj-rest-auth/registration/",
            data={
                "username": "firstuser",
                "email": "firstuser@email.com",
                "password1": "secretpassword",
                "password2": "secretpassword",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


class AuthenticationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.user = get_user_model().objects.create_user(
            username="testuser", email="testuser@email.com", password="secretpassword"
        )

    def test_user_login(self):
        response = self.client.post(
            "/api/v1/dj-rest-auth/login/",
            data={"username": "testuser", "password": "secretpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for auth token in response
        self.assertTrue("key" in response.data)

    def test_user_login_with_incorrect_credentials(self):
        response = self.client.post(
            "/api/v1/dj-rest-auth/login/",
            data={"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure no auth token in response
        self.assertNotIn("key", response.data)

    def test_logout(self):
        self.client.post(
            "/api/v1/dj-rest-auth/login/",
            data={"username": "testuser", "password": "secretpassword"},
        )
        response = self.client.post("/api/v1/dj-rest-auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_when_not_authenticated(self):
        response = self.client.post("/api/v1/dj-rest-auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

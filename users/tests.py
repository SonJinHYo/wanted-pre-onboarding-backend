from django.test import TestCase, modify_settings

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import User

import os
import jwt


class SignInTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("signin")

    def assertResponse(self, response, expected_status, expected_message=None):
        """assert확인 함수

        Args:
            response (HttpResponse): _description_
            expected_status (int): _description_
            expected_message (string, optional): _description_. Defaults to None.
        """
        self.assertEqual(response.status_code, expected_status)
        if expected_message is not None:
            self.assertEqual(response.data, expected_message)

    def test_signin(self):
        test_cases = [
            {
                "data": {
                    "email": "test@example.com",
                    "password": "securepassword",
                },
                "expected_status": status.HTTP_201_CREATED,
                "expected_message": "회원가입 완료",
            },
            {
                "data": {
                    "email": "test@example.com",
                },
                "expected_status": status.HTTP_400_BAD_REQUEST,
            },
            {
                "data": {
                    "email": "test@example.com",
                    "password": "122",
                },
                "expected_status": status.HTTP_400_BAD_REQUEST,
            },
            {
                "data": {
                    "email": "testfail.com",
                    "password": "12121212",
                },
                "expected_status": status.HTTP_400_BAD_REQUEST,
            },
        ]

        for case in test_cases:
            response = self.client.post(self.url, case["data"], format="json")
            self.assertResponse(
                response, case["expected_status"], case.get("expected_message")
            )

            if case.get("check_user_exists"):
                self.assertTrue(
                    User.objects.filter(email=case["data"]["email"]).exists()
                )


class SignInTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("signin")
        self.user = User.objects.create_user(
            username=" ",
            email="test@example.com",
            password="securepassword",
        )
        self.django_key = os.environ.get("DJANGO_SECRET_KEY")

    def test_successful_sign_in(self):
        data = {
            "email": "test@example.com",
            "password": "securepassword",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_failed_sign_in(self):
        data = {
            "email": "test@example.com",
            "password": "wrongpassword",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_missing_fields(self):
        data = {
            "email": "test@example.com",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User


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

    def test_signup(self):
        test_cases = [
            {
                "data": {"email": "test@example.com", "password": "securepassword"},
                "expected_status": status.HTTP_200_OK,
                "expected_message": "회원가입 완료",
            },
            {
                "data": {"email": "test@example.com"},
                "expected_status": status.HTTP_400_BAD_REQUEST,
            },
            {
                "data": {"email": "test@example.com", "password": "122"},
                "expected_status": status.HTTP_400_BAD_REQUEST,
            },
            {
                "data": {"email": "testexample.com", "password": "122"},
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

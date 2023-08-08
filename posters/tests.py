from django.test import TestCase
from rest_framework import exceptions
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Poster, Content
from users.models import User
from datetime import datetime
from django.utils import timezone


class CreatePostersAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("posters_create")

    def test_create_poster_success(self):
        data1 = {
            "title": "Test Title",
            "content": "Test Content",
        }
        response = self.client.post(
            self.url,
            data1,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Poster.objects.count(), 1)
        self.assertEqual(Content.objects.count(), 1)
        self.assertEqual(response.data["message"], "게시글을 생성했습니다")

        data2 = {
            "title": "A" * 50,
            "content": "B" * 900,
        }
        response = self.client.post(self.url, data2, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_poster_missing_fields(self):
        data = {"title": "Test Title"}
        with self.assertRaises(exceptions.ParseError):
            self.client.post(
                self.url,
                data,
                format="json",
            )

    def test_create_poster_title_max_length(self):
        data = {
            "title": "A" * 101,
            "content": "B" * 1001,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Poster.objects.count(), 0)
        self.assertEqual(Content.objects.count(), 0)
        self.assertEqual(
            response.data["message"],
            "제목의 길이를 확인해주세요.(100자 이하)",
        )

        data = {
            "title": "A" * 101,
            "content": "B" * 900,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Poster.objects.count(), 0)
        self.assertEqual(Content.objects.count(), 0)
        self.assertEqual(
            response.data["message"],
            "제목의 길이를 확인해주세요.(100자 이하)",
        )

    def test_create_poster_content_max_length(self):
        data = {
            "title": "Test Title",
            "content": "C" * 1001,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Poster.objects.count(), 0)
        self.assertEqual(Content.objects.count(), 0)
        self.assertEqual(
            response.data["message"],
            "내용의 길이를 확인해주세요.(1000자 이하)",
        )

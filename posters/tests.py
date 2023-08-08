from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from rest_framework import exceptions
from rest_framework import status
from rest_framework.test import APIClient
from .models import Poster, Content
from users.models import User

import os
import time


class CreatePostersAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="securepassword"
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

    # def test_create_poster_missing_fields(self):
    #     data = {"title": "Test Title"}
    #     with self.assertRaises(exceptions.ParseError):
    #         self.client.post(
    #             self.url,
    #             data,
    #             format="json",
    #         )

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


class PostersAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=" ", email="testuser@example.com", password="securepassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.base_url = reverse("posters")

        self.total_poster = 49
        self.page_size = settings.PAGE_SIZE
        self.last_page = self.total_poster // self.page_size + 1
        self.rem_page = self.total_poster % self.page_size

        for i in range(1, self.total_poster + 1):
            Poster.objects.create(
                user=self.user,
                title=f"Test Poster {i}",
                created_at=timezone.now().replace(microsecond=0),
                updated_at=timezone.now().replace(microsecond=0),
            )

    def test_get_posters_success(self):
        for page in range(1, self.last_page + 1):
            url = os.path.join(self.base_url, f"?page={page}")
            response = self.client.get(url, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            if page < self.last_page:
                self.assertEqual(len(response.data), self.page_size)
            else:
                self.assertEqual(len(response.data), self.rem_page)


class PosterDetailAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=" ", email="testuser@example.com", password="securepassword"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.poster = Poster.objects.create(
            user=self.user,
            title="Test Poster",
            created_at=timezone.now().replace(microsecond=0),
            updated_at=timezone.now().replace(microsecond=0),
        )
        self.content = Content.objects.create(
            poster=self.poster,
            text="Test Content",
        )
        self.url = reverse("poster_detail", args=[self.poster.pk])

    def test_get_poster_detail(self):
        response = self.client.get(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Poster")

    def test_update_poster_detail(self):
        updated_content = "Updated Content"

        response = self.client.put(
            self.url,
            {"content": updated_content},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"]["text"], updated_content)

    def test_update_poster_detail_unauthorized(self):
        other_user = User.objects.create_user(
            username=" ", email="otheruser@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.put(
            self.url,
            {"content": "Updated Content"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_poster_detail_no_content(self):
        response = self.client.put(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "내용을 작성해주세요")

    def test_delete_poster_detail(self):
        response = self.client.delete(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Poster.objects.count(), 0)

    def test_delete_poster_detail_unauthorized(self):
        other_user = User.objects.create_user(
            username="otheruser", email="otheruser@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(self.url, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Poster.objects.count(), 1)

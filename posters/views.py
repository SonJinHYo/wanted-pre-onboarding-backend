from django.utils import timezone
from django.db import transaction

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from . import serializers
from .models import Content
from users.models import User


class Posters(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        content = request.data.get("content")
        user = request.user
        if not title or not content:
            return exceptions.ParseError("제목과 내용을 모두 입력해주세요")

        poster_serializer = serializers.PosterSerializer(
            data={
                "title": title,
                "created_at": timezone.localtime(),
                "updated_at": timezone.localtime(),
            }
        )

        if poster_serializer.is_valid():
            with transaction.atomic():
                new_poster = poster_serializer.save(
                    user=user,
                )
                Content.objects.create(poster=new_poster, content=content)

            return Response(
                {
                    "message": "게시글을 생성했습니다",
                    "title": new_poster.title,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                "제목과 내용의 길이를 확인해주세요.(제목 100자 이하, 내용 1000자 이하)",
                status=status.HTTP_400_BAD_REQUEST,
            )

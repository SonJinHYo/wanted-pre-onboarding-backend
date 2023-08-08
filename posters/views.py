from django.utils import timezone
from django.db import transaction

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from . import serializers
from .models import Content, Poster
from users.models import User

from django.conf import settings


class CreatePosters(APIView):
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
                {"meesage": "제목과 내용의 길이를 확인해주세요.(제목 100자 이하, 내용 1000자 이하)"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Posters(APIView):
    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start, end = (page - 1) * page_size, page * page_size

        serializer = serializers.PosterListSerializer(
            Poster.objects.all()[start:end],
            many=True,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class PosterDetail(APIView):
    def get_object(self, pk):
        try:
            return Poster.objects.get(pk=pk)
        except Poster.DoesNotExist:
            raise exceptions.NotFound

    def get(self, request, pk):
        poster = self.get_object(pk)
        serializer = serializers.PosterDetailSerializer(poster)
        return Response(serializer.data)

    def put(self, request, pk):
        poster = self.get_object(pk)
        if poster.user == request.user:
            content = poster.contents
            print(content)
            print(type(content))
            content_serializer = serializers.ConetentSerializer(
                content,
                data={
                    "content": request.data["content"],
                },
                partial=True,
            )
            if content_serializer.is_valid():
                poster.updated_at = timezone.now()
                with transaction.atomic():
                    content_serializer.save()
                    poster.save()
                return Response(
                    serializers.PosterDetailSerializer(poster).data,
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "게시물 내용의 길이를 확인해주세요. (1000자 이하)"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            raise exceptions.AuthenticationFailed("권한이 없습니다.")

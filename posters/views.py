from django.utils import timezone
from django.db import transaction

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from . import serializers
from .models import Content, Poster

from django.conf import settings


class CreatePosters(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        title = request.data.get("title")
        content = request.data.get("content")
        user = request.user

        if title is None or content is None:
            raise exceptions.ParseError("제목과 내용을 모두 입력해주세요")

        poster_serializer = serializers.PosterSerializer(
            data={
                "title": title,
                "created_at": timezone.localtime().replace(microsecond=0),
                "updated_at": timezone.localtime().replace(microsecond=0),
            }
        )

        if poster_serializer.is_valid():
            with transaction.atomic():
                contents_serializer = serializers.ConetentSerializer(
                    data={"text": content}
                )

                if contents_serializer.is_valid():
                    new_poster = poster_serializer.save(user=user)
                    contents_serializer.save(poster=new_poster)

                else:
                    return Response(
                        {"message": "내용의 길이를 확인해주세요.(1000자 이하)"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            return Response(
                {"message": "게시글을 생성했습니다"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "제목의 길이를 확인해주세요.(100자 이하)"},
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
            raise exceptions.NotFound("존재하지 않는 게시글입니다.")

    def get(self, request, pk):
        poster = self.get_object(pk)
        serializer = serializers.PosterDetailSerializer(poster)
        return Response(serializer.data)

    def put(self, request, pk):
        poster = self.get_object(pk)

        if poster.user != request.user:
            raise exceptions.AuthenticationFailed("권한이 없습니다.")

        text = request.data.get("content")
        if text is None:
            return Response(
                {"message": "내용을 작성해주세요"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        contents = poster.contents
        contents_serializer = serializers.ConetentSerializer(
            contents,
            data={"text": text},
            partial=True,
        )

        if contents_serializer.is_valid():
            with transaction.atomic():
                contents_serializer.save()
                poster.updated_at = timezone.now().replace(microsecond=0)
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

    def delete(self, request, pk):
        poster = self.get_object(pk)

        if poster.user != request.user:
            raise exceptions.AuthenticationFailed("권한이 없습니다.")

        poster.delete()
        return Response(
            {"message": "게시글이 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )

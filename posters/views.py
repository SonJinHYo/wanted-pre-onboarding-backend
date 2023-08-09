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
    """게시글(Poster) 생성 APIView

    Parameters:
        permission_classes: 유저 로그인(권한) 확인

    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """게시글 생성 post 요청 처리 함수

        Parameters:
            title (str): 게시글 제목
            content (str): 게시글 내용
            user (users.models.User) : 로그인한 유저 객체

        Raises:
            exceptions.ParseError: title 또는 content 누락 에러

        Returns:
            Response: 게시물()
        """
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
    """전체 포스터 APIView"""

    def get(self, request):
        """전체 포스터 pagination view. Content 쿼리 X

        Parameters:
            page (int): api 파라미터로 받는 페이지 수
            start (int): Poster 객체 슬라이싱 시작 인덱스
            end (int): Poster 객체 슬라이싱 마지막 인덱스

        Returns:
            Response: 페이지에 따른 Poster객체 반환
        """
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
    """특정 Poster APIView

    Args:
        pk (int): api로 받는 특정 Poster의 pk값

    """

    def get_object(self, pk):
        """특정 Poster 객체 반환 함수"""
        try:
            return Poster.objects.get(pk=pk)
        except Poster.DoesNotExist:
            raise exceptions.NotFound("존재하지 않는 게시글입니다.")

    def get(self, request, pk):
        """pk에 해당하는 Poster get 요청 처리"""
        poster = self.get_object(pk)
        serializer = serializers.PosterDetailSerializer(poster)
        return Response(serializer.data)

    def put(self, request, pk):
        """pk에 해당하는 Poster post 요청 처리

        Parameters:
            poster (models.Poster): pk에 해당하는 poster객체
            contents (models.Content): pk에 해당하는 poster객체의 Contents 객체
            text (str): contents 객체의 내용(게시글의 본문)

        Raises:
            exceptions.AuthenticationFailed: 게시글 주인이 아닐시 예외 처리

        Returns:
            Response: 수정된 게시글 반환
        """
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
        """pk에 해당하는 Poster delete 요청 처리

        Parameters:
            poster (models.Poster): pk에 해당하는 poster객체

        Raises:
            exceptions.AuthenticationFailed: 게시글 주인이 아닐시 예외 처리

        Returns:
            Response: 삭제 메세지 반환
        """
        poster = self.get_object(pk)

        if poster.user != request.user:
            raise exceptions.AuthenticationFailed("권한이 없습니다.")

        poster.delete()
        return Response(
            {"message": "게시글이 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )

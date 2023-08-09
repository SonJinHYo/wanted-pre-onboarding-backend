from rest_framework.serializers import ModelSerializer
from .models import Poster, Content
from users.serializers import TinyUserSerializer


class PosterSerializer(ModelSerializer):
    # 포스터 생성시 사용

    user = TinyUserSerializer(
        read_only=True,
    )

    class Meta:
        model = Poster
        fields = (
            "user",
            "title",
            "created_at",
            "updated_at",
        )


class ConetentSerializer(ModelSerializer):
    # contents(게시글 내용) 필요시 사용

    class Meta:
        model = Content
        fields = ("text",)


class PosterDetailSerializer(ModelSerializer):
    # 특정 Poster 접근 시 사용

    user = TinyUserSerializer(
        read_only=True,
    )
    content = ConetentSerializer(
        source="contents",
        read_only=True,
    )

    class Meta:
        model = Poster
        fields = (
            "user",
            "title",
            "content",
            "created_at",
            "updated_at",
        )


class PosterListSerializer(ModelSerializer):
    # 게시글 목록을 불러올 때 사용

    user = TinyUserSerializer(
        read_only=True,
    )

    class Meta:
        model = Poster
        fields = (
            "user",
            "title",
            "updated_at",
        )

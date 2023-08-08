from rest_framework.serializers import ModelSerializer
from .models import Poster, Content
from users.serializers import TinyUserSerializer


class PosterSerializer(ModelSerializer):
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
    class Meta:
        model = Content
        fields = ("content",)

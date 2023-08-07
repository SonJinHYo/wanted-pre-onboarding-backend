from rest_framework.serializers import ModelSerializer
from .models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
        )

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        new_user = self.Meta.model(**validated_data)

        if password is not None:
            new_user.set_password(password)
        new_user.save()

        return new_user

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import exceptions
from rest_framework.response import Response
from django.contrib.auth import authenticate

from django.conf import settings
from . import serializers

import jwt


# Create your views here.
class SignIn(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            raise exceptions.ParseError("email과 password를 모두 입력해주세요.")

        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            serializer = serializers.UserSerializer(user)
            return Response("회원가입 완료", status=status.HTTP_201_CREATED)
        else:
            return Response(
                "회원가입 실패. 패스워드가 8자 미만이거나 이미 이미 존재하는 email입니다.",
                status=status.HTTP_400_BAD_REQUEST,
            )


class JWTLogIn(APIView):
    def generate_token(self, user):
        payload = {"pk": user.pk}
        key = settings.SECRET_KEY
        token = jwt.encode(payload=payload, key=key, algorithm="HS256")
        return token

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            raise exceptions.ParseError("email과 password를 모두 입력해주세요.")

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if user:
            token = self.generate_token(user)
            return Response({"token": token}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "유효하지 않은 email과 password 조합입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

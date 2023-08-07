from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import exceptions
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout


from . import serializers

import jwt
import os


# Create your views here.
class SignIn(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            raise exceptions.ParseError

        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            serializer = serializers.UserSerializer(user)
            return Response("회원가입 완료", status=status.HTTP_200_OK)
        else:
            return Response(
                "회원가입 실패. 패스워드가 8자 미만이거나 이미 이미 존재하는 email입니다.",
                status=status.HTTP_400_BAD_REQUEST,
            )


class JWTLogIn(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            raise exceptions.ParseError

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if user:
            token = jwt.encode(
                payload={"pk": user.pk},
                key=os.environ.get("DJANGO_SECRET_KEY"),
                algorithm="HS256",
            )
            return Response({"token": token}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "email과 password를 다시 확인하세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

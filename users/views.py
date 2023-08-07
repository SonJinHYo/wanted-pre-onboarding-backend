from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import exceptions
from rest_framework.response import Response
from . import serializers


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
            return Response("회원가입 실패. email과 password(8자 이상)를 알맞게 입력해주세요")

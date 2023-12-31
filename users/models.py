from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    # 관리자 계정에 설정된 username 테이블 처리를 위한 필드
    username = models.CharField(
        blank=True,
        null=True,
        max_length=100,
    )
    email = models.EmailField(
        unique=True,
    )
    password = models.CharField(
        max_length=128,
        validators=[MinLengthValidator(8)],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

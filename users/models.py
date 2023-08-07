from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator


class User(AbstractUser):
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
        validators=[MinLengthValidator],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "password"]

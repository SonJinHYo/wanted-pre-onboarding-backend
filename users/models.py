from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
    )
    password = models.CharField(
        max_length=128,
        validators=[MinLengthValidator],
    )

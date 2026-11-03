from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants import ZODIAC_CHOICES


class User(AbstractUser):
    """Пользователь: логин (username), хеш пароля (password) и знак зодиака."""

    zodiac_sign = models.CharField(
        'Знак зодиака', max_length=20, choices=ZODIAC_CHOICES, blank=True
    )

    class Meta:
        db_table = 'users'
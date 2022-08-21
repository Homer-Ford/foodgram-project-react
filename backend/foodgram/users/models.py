from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель для создания таблицы пользователей."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name_plural = 'User'

    def __str__(self):
        return self.username

from django.db import models

# Create your models here.
import os.path

from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import get_user_avatar_path

# Create your models here.
class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True,  # Уникальность хороша, чтобы не привязать два аккаунта к одному боту
        verbose_name='Telegram ID'
    )
    # Telegram Username (никнейм без @)
    tg_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Telegram Username',
        help_text='Ваш ник в Телеграмм'
    )

    country = models.CharField(max_length=25, blank=True, null=True)
    avatar = models.ImageField(
        upload_to='user_avatars/',
        # upload_to=get_user_avatar_path,
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text='Ваше фото'
    )
    is_email_verified = models.BooleanField(default=False, verbose_name='Email подтверждён')
    # Флаг: заблокирован ли пользователь в плане функционала рассылок
    is_blocked = models.BooleanField(default=False, verbose_name='Заблокирован (нет доступа к рассылкам)')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]
        # Гарантируем уникальность email на уровне БД
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email_constraint')
        ]

    def __str__(self):
        if self.username:
            return self.username
        if self.email:
            return self.email
        return f"Пользователь #{self.id}"

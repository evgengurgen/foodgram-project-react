from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_backend.constants import MAX_NAME_LENGTH


class MyUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name='Блокировка',
        help_text='Заблокирован ли пользователь'
    )
    username = models.CharField(
        max_length=MAX_NAME_LENGTH,
        unique=True,
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Фамилия'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user__username',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

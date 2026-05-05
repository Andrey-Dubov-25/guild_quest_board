from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core import constants


class User(AbstractUser):
    """
    Модель юзера с дополнительными полями:
    - роль (role - tavern_keeper, adventurer)
    - уровень персонажа (level)
    """
    class UserRoles(models.TextChoices):
        """Доступные роли для юзера."""
        TAVERN_KEEPER = 'tavern_keeper'
        ADVENTURER = 'adventurer'

    email = models.EmailField(
        max_length=constants.EMAIL_LEN,
        unique=True,
        verbose_name='Электронная почта',
        help_text='Электронная почта пользователя'
    )
    username = models.CharField(
        max_length=constants.USERNAME_LEN,
        unique=True,
        verbose_name='Ник',
        help_text='Виртуальное имя пользователя'
    )
    role = models.CharField(
        max_length=max(len(role[0]) for role in UserRoles.choices),
        choices=UserRoles.choices,
        default=UserRoles.ADVENTURER,
        verbose_name='Роль',
        help_text='Уровень доступа: трактильщик, авантюрист',
    )
    level = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(constants.MIN_MEANING_FOR_VALIDATOR_SCORE),
            MaxValueValidator(constants.MAX_MEANING_FOR_VALIDATOR_SCORE),
        ],
        verbose_name='Уровень',
        help_text='Уровень персонажа (только для авантюристов)'
    )
    password = models.CharField(
        max_length=constants.PASSWORD_LEN,
        verbose_name='Пароль',
        help_text='Пароль пользователя'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def is_adventurer(self):
        """Проверяет, является ли пользователь авантюристом."""
        return self.role == self.UserRoles.ADVENTURER

    def is_tavern_keeper(self):
        """Проверяет, является ли пользователь трактильщиком."""
        return self.role == self.UserRoles.TAVERN_KEEPER

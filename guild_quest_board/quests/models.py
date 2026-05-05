from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core import constants


User = get_user_model()


class QuestType(models.Model):
    """Модель типов квеста."""

    name = models.CharField(
        max_length=constants.NAME_QUEST_TYPE_LEN,
        verbose_name='Название',
        help_text='Название типа квеста'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание',
        help_text='Описание типа квеста'
    )

    class Meta:
        verbose_name = 'тип квеста'
        verbose_name_plural = 'Типы квестов'

    def __str__(self):
        return self.name


class Quest(models.Model):
    """Модель квеста."""
    class QuestStatus(models.TextChoices):
        """Доступные статусы."""
        AVAILABLE = 'available'
        IN_PROGRESS = 'in_progress'
        COMPLETED = 'completed'
        FAILED = 'failed'
        CANCELLED = 'cancelled'

    name = models.CharField(
        max_length=constants.NAME_QUEST_LEN,
        verbose_name='Название',
        help_text='Название квеста'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание квеста'
    )
    quest_type = models.ForeignKey(
        QuestType,
        on_delete=models.CASCADE,
        related_name='quests',
        verbose_name='Тип квеста',
        help_text='Тип для квеста'
    )
    min_level = models.PositiveSmallIntegerField(
        verbose_name='Уровень',
        help_text='Уровень доступа для персонажа (только для авантюристов)',
        validators=[
            MinValueValidator(constants.MIN_MEANING_FOR_VALIDATOR_SCORE),
            MaxValueValidator(constants.MAX_MEANING_FOR_VALIDATOR_SCORE),
        ]
    )
    reward = models.CharField(
        max_length=constants.AWARD_LEN,
        verbose_name='Награда',
        help_text='Награда за выполнение квеста'
    )
    status = models.CharField(
        max_length=max(len(status[0]) for status in QuestStatus.choices),
        choices=QuestStatus.choices,
        default=QuestStatus.AVAILABLE,
        verbose_name='Статус',
        help_text='Текущий статус квеста',
    )
    adventurer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_quests',
        verbose_name='Исполнитель',
        help_text='Исполнитель квеста'
    )
    monster = models.CharField(
        max_length=constants.MONSTER_LEN,
        verbose_name='Монстр',
        help_text='Монстр для квеста'
    )

    class Meta:
        verbose_name = 'квест'
        verbose_name_plural = 'Квесты'

    def __str__(self):
        return self.name


class QuestReport(models.Model):
    """Модель отчета."""
    class EndQuestResult(models.TextChoices):
        """Результат квеста."""
        SUCCESS = 'success'
        FAILURE = 'failure'

    quest = models.ForeignKey(
        Quest,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='Квест',
        help_text='Отчет к квесту'
    )
    adventurer = models.ForeignKey(
        User,
        related_name='quest_reports',
        on_delete=models.CASCADE,
        verbose_name='Авантюрист',
        help_text='Автор отчета'
    )
    result = models.CharField(
        max_length=max(len(status[0]) for status in EndQuestResult.choices),
        choices=EndQuestResult.choices,
        verbose_name='Результат',
        help_text='Результат выполнения квеста'
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        help_text='Комментарий авантюриста'
    )

    class Meta:
        verbose_name = 'отчет'
        verbose_name_plural = 'Отчеты'

    def __str__(self):
        return f'Отчет по квесту {self.quest.name}'

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from core import constants, utils
from quests.models import (
    Quest,
    QuestReport,
    QuestType,
    User
)


class UserSerializer(serializers.ModelSerializer):
    """Сериализация данных пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'role'
        )
        ref_name = 'CustomUser'


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализация данных при регистрации пользователя."""

    email = serializers.EmailField(max_length=constants.EMAIL_LEN)
    username = serializers.CharField(max_length=constants.USERNAME_LEN)
    first_name = serializers.CharField(max_length=constants.FIRST_NAME_LEN)
    last_name = serializers.CharField(max_length=constants.LAST_NAME_LEN)
    password = serializers.CharField(
        max_length=constants.PASSWORD_LEN, write_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate(self, data):
        """
        Валидация существования email или usermname, которые указаны при
        регистрации.
        """
        username = utils.get_username(data)
        email = utils.get_email(data)
        username_for_user = User.objects.filter(
            username=username
        ).first()
        email_for_user = User.objects.filter(email=email).first()

        if username_for_user:
            raise serializers.ValidationError(
                'Пользователь с таким username уже зарегистрирован.'
            )
        if email_for_user:
            raise serializers.ValidationError(
                'Email уже используется другим пользователем.'
            )

        return data

    def create(self, validated_data):
        """Создание нового пользователя."""
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class GetTokenSerializer(serializers.Serializer):
    """Сериализация данных при получении токена."""

    email = serializers.CharField(
        required=True, max_length=constants.EMAIL_LEN
    )
    password = serializers.CharField(
        required=True, max_length=constants.PASSWORD_LEN
    )

    def validate(self, data):
        """
        Валидация соответствия пароля.
        """
        email = data['email']
        password = data['password']
        user = get_object_or_404(User, email=email)

        if not user.check_password(password):
            raise serializers.ValidationError('Неверный пароль')
        data['user'] = user
        return data


class QuestTypeSerializer(serializers.ModelSerializer):
    """Сериализация данных для типов квестов."""

    class Meta:
        model = QuestType
        fields = ('name', 'description')


class QuestSerializer(serializers.ModelSerializer):
    """Сериализация данных для квестов."""

    class Meta:
        model = Quest
        fields = (
            'name',
            'description',
            'quest_type',
            'min_level',
            'reward',
            'status',
            'adventurer',
            'monster'
        )


class QuestReportSerializer(serializers.ModelSerializer):
    """Сериализация данных для отчетов квестов."""

    class Meta:
        model = QuestReport
        fields = ('quest', 'adventurer', 'result', 'comment')


class QuestCreateSerializer(serializers.ModelSerializer):
    """Сериализация данных для создания квестов."""

    class Meta:
        model = Quest
        fields = (
            'name',
            'description',
            'quest_type',
            'reward',
            'min_level'
        )

    def validate_min_level(self, value):
        """Валидация минимального уровня. Не должно быть меньше 0"""
        if value < 1:
            raise serializers.ValidationError('Уровень должен быть больше 0')

        return value


class QuestCancelledSerializer(serializers.Serializer):
    """Сериализация данных для отмены квестов."""

    def validate(self, data):
        """Валидация статуса квеста и роль тавернщика."""
        quest = utils.get_quest(self)
        user = utils.get_user(self)

        if quest.status != Quest.QuestStatus.AVAILABLE:
            raise serializers.ValidationError(
                'Нельзя отменить квест не в статусе available.'
            )

        if not user.is_tavern_keeper():
            raise serializers.ValidationError(
                'Отменить квест может только тавернщик'
            )

        return data


class QuestTakeSerializer(serializers.Serializer):
    """Сериализация данных для взятия квеста в работу."""

    def validate(self, data):
        """
        Валидация статуса и доступности квеста для работы:
        - квест не в статусе `available`;
        - квест уже взят другим пользователем;
        - уровень пользователя ниже требуемого;
        - у пользователя уже 3 квеста в работе.
        """
        quest = utils.get_quest(self)
        user = utils.get_user(self)

        if quest.status != Quest.QuestStatus.AVAILABLE:
            raise serializers.ValidationError(
                'Квест не в статусе available и поэтому его нельзя взять.'
            )

        if quest.adventurer is not None:
            raise serializers.ValidationError(
                f'Квест уже взял {quest.adventurer}'
            )

        if user.level < quest.min_level:
            raise serializers.ValidationError(
                f'Для выполнения квеста нужен уровень от {quest.min_level}'
            )

        adventurer_quests_count = Quest.objects.filter(
            adventurer=user,
            status=Quest.QuestStatus.IN_PROGRESS
        ).count()

        if adventurer_quests_count >= 3:
            raise serializers.ValidationError('Нельзя брать больше 3 квестов')

        return data


class QuestCompletedSerializer(serializers.Serializer):
    """Сериализация данных для завершения квеста."""

    result = serializers.ChoiceField(choices=['success', 'failed'])
    comment = serializers.CharField(
        max_length=constants.COMMENT_LEN, required=False, allow_blank=True
    )

    def validate(self, data):
        """
        Валидация статуса и доступности квеста для завершения:
        - квест не в статусе in_progress;
        - квест уже завершён;
        - квест принадлежит другому пользователю.
        """
        quest = utils.get_quest(self)
        user = utils.get_user(self)

        if quest.status != Quest.QuestStatus.IN_PROGRESS:
            raise serializers.ValidationError(
                'Нельзя завершить квест не в статусе in_progress.'
            )

        if quest.status in [
            Quest.QuestStatus.COMPLETED, Quest.QuestStatus.FAILED
        ]:
            raise serializers.ValidationError(
                'Квест уже завершён.'
            )

        if quest.adventurer != user:
            raise serializers.ValidationError(
                'Нельзя завершить чужой квест.'
            )

        return data

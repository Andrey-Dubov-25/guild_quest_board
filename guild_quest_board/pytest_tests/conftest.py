import pytest
from rest_framework.test import APIClient

from quests.models import Quest, QuestType, QuestReport


@pytest.fixture
def adventurer(django_user_model):
    """Фикстура создания авантюриста."""
    user = django_user_model.objects.create_user(
        username='Andr',
        first_name='Abdrey',
        last_name='Tester',
        email='test_adventurer@gmail.com',
        password='3f5h7m0a'
    )
    return user


@pytest.fixture
def adventurer_author(django_user_model):
    """Фикстура создания авантюриста."""
    user = django_user_model.objects.create_user(
        username='Author',
        first_name='Anton',
        last_name='Tes',
        email='advent@gmail.com',
        password='3f5h7m0a'
    )
    return user


@pytest.fixture
def adventurer_not_author(django_user_model):
    """Фикстура создания авантюриста."""
    user = django_user_model.objects.create_user(
        username='NotAuthor',
        first_name='NotAnton',
        last_name='NotTes',
        email='noadvent@gmail.com',
        password='3f5h7m0a'
    )
    return user


@pytest.fixture
def adventurer_data_for_token(adventurer):
    """
    Фикстура данных для получения токена:
    - email;
    - password.
    """
    data = {
        'email': adventurer.email,
        'password': '3f5h7m0a'
    }
    return data


@pytest.fixture
def tavern_keeper(django_user_model):
    """Фикстура создания тавернщика."""
    user = django_user_model.objects.create(
        username='Andr',
        first_name='Abdrey',
        last_name='Tester',
        email='test_tavern@gmail.com',
        password='3f5h7m0a',
        role='tavern_keeper'
    )
    return user


@pytest.fixture
def adventurer_client(adventurer):
    """Фикстура авторизованного авантюриста."""
    client = APIClient()
    client.force_authenticate(adventurer)
    return client


@pytest.fixture
def adventurer_author_client(adventurer_author):
    """Фикстура авторизованного авантюриста."""
    client = APIClient()
    client.force_authenticate(adventurer_author)
    return client


@pytest.fixture
def adventurer_not_author_client(adventurer_not_author):
    """Фикстура авторизованного авантюриста."""
    client = APIClient()
    client.force_authenticate(adventurer_not_author)
    return client


@pytest.fixture
def tavern_keeper_client(tavern_keeper):
    """Фикстура авторизованного тавернщика."""
    client = APIClient()
    client.force_authenticate(tavern_keeper)
    return client


@pytest.fixture
def quest_type_data():
    """
    Фикстура данных для создания типа квеста:
    - name;
    - description.
    """
    data = {
        'name': 'Новый типt',
        'description': 'Новый тип квеста'
    }
    return data


@pytest.fixture
def quest_type():
    """Фикстура создания типа квеста."""
    quest_type = QuestType.objects.create(
        name='hunt',
        description='Охота'
    )
    return quest_type


@pytest.fixture
def quest(quest_type):
    """Фикстура создания квеста."""
    quest = Quest.objects.create(
        name='Поход',
        description='Текст',
        quest_type=quest_type,
        reward='Награда',
        min_level=1,
        monster='TestMonster'
    )
    return quest


@pytest.fixture
def quest_author(quest_type, adventurer_author):
    """Фикстура создания квеста."""
    quest = Quest.objects.create(
        name='Поход',
        description='Текст',
        quest_type=quest_type,
        reward='Награда',
        status=Quest.QuestStatus.IN_PROGRESS,
        min_level=1,
        monster='TestMonster',
        adventurer=adventurer_author
    )
    return quest


@pytest.fixture
def quest_report():
    """Фикстура создания отчета о квесте."""
    quest_report = QuestReport.objects.create(
        quest=1,
        adventurer=1,
        result='success',
        comment='Комментарий'
    )
    return quest_report


@pytest.fixture
def quest_data(quest_type):
    """
    Фикстура данных для создания квеста:
    - name;
    - description;
    - quest_type;
    - reward;
    - min_level.
    """
    data = {
        'name': 'Мореплавание',
        'description': 'Новый текст',
        'quest_type': quest_type.id,
        'reward': 'Новая награда',
        'min_level': 1
    }
    return data


@pytest.fixture
def user_data():
    """
    Фикстура данных для регистрации нового пользователя:
    - email;
    - username;
    - first_name;
    - last_name;
    - password.
    """
    data = {
        "email": "user@example.com",
        "username": "TestUser",
        "first_name": "User",
        "last_name": "UserTest",
        "password": "TestPassword"
    }
    return data


@pytest.fixture
def data_for_quest_report():
    """
    Фикстура данных для завершения квеста со статусом success:
    - result;
    - comment.
    """
    data = {
        "result": "success",
        "comment": "string"
    }
    return data

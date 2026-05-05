from django.urls import reverse
from http import HTTPStatus
from pytest_lazy_fixtures import lf
import pytest

from quests.models import Quest


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (lf('adventurer_client'), HTTPStatus.FORBIDDEN),
        (lf('tavern_keeper_client'), HTTPStatus.CREATED),
        (lf('client'), HTTPStatus.UNAUTHORIZED)
    )
)
def test_create_quest(quest_data, parametrized_client, status):
    """
    Тестирование создание квеста:
    - тавернщик может создать квест (201),
    - авантюрист не может создать квест (403),
    - анонимный пользователь не может создать квест (401).
    """
    url = reverse('api:quests-list')
    response = parametrized_client.post(url, quest_data)
    assert response.status_code == status


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (lf('adventurer_client'), HTTPStatus.FORBIDDEN),
        (lf('tavern_keeper_client'), HTTPStatus.CREATED),
        (lf('client'), HTTPStatus.UNAUTHORIZED)
    )
)
def test_create_quest_type(quest_type_data, parametrized_client, status):
    """
    Тестирование создание типа квеста:
    - тавернщик может создать квест (201);
    - авантюрист не может создать квест (403);
    -анонимный пользователь не может создать квест (401).
    """
    url = reverse('api:quest-types-list')
    response = parametrized_client.post(url, quest_type_data)
    assert response.status_code == status


def test_create_user(user_data, client):
    """Тестирование регистрации пользователя."""
    url = reverse('api:users-list')
    response = client.post(url, user_data)
    assert response.status_code == HTTPStatus.CREATED


def test_get_token_user(client, adventurer_data_for_token):
    """Тестирование получения токена после регистрации."""
    url = reverse('api:token')
    response = client.post(url, adventurer_data_for_token)
    assert response.status_code == HTTPStatus.OK
    assert 'token' in response.data


def test_take_quest_for_adventurer(quest, adventurer_client):
    """
    Тестирование взятие квеста авантюристом в работу - статус квеста меняестя с
    'available' на 'in_progress (200).
    """
    url = reverse('api:quests-take', kwargs={'pk': quest.id})
    response = adventurer_client.patch(url)
    assert quest.status == Quest.QuestStatus.AVAILABLE
    quest.refresh_from_db()
    assert response.status_code == HTTPStatus.OK
    assert quest.status == Quest.QuestStatus.IN_PROGRESS
    assert quest.adventurer == adventurer_client.handler._force_user


def test_take_quest_for_tavern_keeper(quest, tavern_keeper_client):
    """
    Тестирование взятие квеста тавернщиком в работу - запрещено (403).
    """
    url = reverse('api:quests-take', kwargs={'pk': quest.id})
    response = tavern_keeper_client.patch(url)
    assert quest.status == Quest.QuestStatus.AVAILABLE
    quest.refresh_from_db()
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert quest.status == Quest.QuestStatus.AVAILABLE


@pytest.mark.parametrize(
    'parametrized_client, status',
    (
        (lf('adventurer_client'), HTTPStatus.FORBIDDEN),
        (lf('tavern_keeper_client'), HTTPStatus.NO_CONTENT),
        (lf('client'), HTTPStatus.UNAUTHORIZED)
    )
)
def test_delete_quest_for_tavern_keeper(quest, parametrized_client, status):
    """
    Тестирование удаления квеста:
    - тавернщик может удалить квест (204),
    - авантюрист не можнт удалить квест (403),
    - анонимный пользователь не может удалить квест (401).
    """
    url = reverse('api:quests-detail', kwargs={'pk': quest.id})
    response = parametrized_client.delete(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'parametrized_client, status_response, status_before, status_after',
    (
        (
            lf('adventurer_not_author_client'),
            HTTPStatus.BAD_REQUEST,
            Quest.QuestStatus.IN_PROGRESS,
            Quest.QuestStatus.IN_PROGRESS
        ),
        (
            lf('adventurer_author_client'),
            HTTPStatus.OK,
            Quest.QuestStatus.IN_PROGRESS,
            Quest.QuestStatus.COMPLETED
        ),
    )
)
def test_completed_quest(
    quest_author,
    parametrized_client,
    status_response,
    status_before,
    status_after,
    data_for_quest_report
):
    """
    Тестирование завершения квеста авантюристом:
    - авантюрист может завершить свой квест (200);
    - авантюрист не может завершить чужой квест (400);
    - при успешном обновлении статус квеста меняется с 'in_progress' на
    'completed' (квест завершается со статусом 'success).
    """
    url = reverse('api:quests-completed', kwargs={'pk': quest_author.id})
    response = parametrized_client.post(url, data_for_quest_report)
    assert quest_author.status == status_before
    quest_author.refresh_from_db()
    assert response.status_code == status_response
    assert quest_author.status == status_after

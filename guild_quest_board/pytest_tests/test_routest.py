from django.urls import reverse
from http import HTTPStatus
from pytest_lazy_fixtures import lf
import pytest


@pytest.mark.parametrize(
    'url, expected_status',
    (
        ('api:quests-list', HTTPStatus.UNAUTHORIZED),
        ('api:quest-types-list', HTTPStatus.UNAUTHORIZED),
    )
)
def test_quests_for_anonymous(client, url, expected_status):
    """
    Тестирование доступности страницы квестов и их типов для анонима:
    - аноним не может получит страницы (401).
    """
    url = reverse(url)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'parametrized_client, expected_status', (
        (lf('adventurer_client'), HTTPStatus.OK),
        (lf('tavern_keeper_client'), HTTPStatus.OK),
        (lf('client'), HTTPStatus.UNAUTHORIZED),
    )
)
def test_users_me_for_authenticated_user(parametrized_client, expected_status):
    """
    Тестирование доступности страницы пользователя:
    - тавернщик может получть информацию о себе (200);
    - авантюрист может получить информацию о себе (200);
    - анонимный пользователь не может получить информацию о себе (401).
    """
    url = reverse('api:users-me')
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'parametrized_client, expected_status', (
        (lf('adventurer_client'), HTTPStatus.FORBIDDEN),
        (lf('tavern_keeper_client'), HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'url',
    ('api:quest-types-list',)
)
def test_quest_types_list(
    parametrized_client, expected_status, url
):
    """
    Тестирование доступности страницы типов квестов для авантюриста и
    тавернщика:
    - тавернщик может получить страницу типов квестов (200);
    - авантюрист не может получить страницу типов квестов (403)
    """
    url = reverse(url)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'parametrized_client, expected_status', (
        (lf('adventurer_client'), HTTPStatus.OK),
        (lf('tavern_keeper_client'), HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'url',
    ('api:quests-list',)
)
def test_quests_list(
    parametrized_client, expected_status, url
):
    """
    Тестирование доступности страницы квестов для авантюриста и
    тавернщика - оба имеют доступ (200).
    """
    url = reverse(url)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status

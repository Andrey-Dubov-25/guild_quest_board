from django.urls import reverse
from pytest_lazy_fixtures import lf
import pytest


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'parametrized_client, quest_in_list',
    (
        (lf('tavern_keeper_client'), True),
        (lf('adventurer_client'), True)
    )
)
def test_quest_in_list_for_adventurer(
    quest, parametrized_client, quest_in_list
):
    """Тестирование наличие квеста в запросе к странице квестов."""
    url = reverse('api:quests-list')
    response = parametrized_client.get(url)
    quest_data = response.data[0]
    assert (quest.name == quest_data['name']) == quest_in_list
    assert (quest.description == quest_data['description']) == quest_in_list
    assert (quest.min_level == quest_data['min_level']) == quest_in_list
    assert (quest.reward == quest_data['reward']) == quest_in_list
    assert (quest.status == quest_data['status']) == quest_in_list
    assert (quest.quest_type.id == quest_data['quest_type']) == quest_in_list
    assert (quest.monster == quest_data['monster']) == quest_in_list

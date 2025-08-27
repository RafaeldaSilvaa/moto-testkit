import pytest

from aws_testkit.examples.event_bridge.synchronous.eventbridge_synchronous_repository import \
    EventBridgeRepository
from aws_testkit.src import MotoTestKit


@pytest.fixture
def moto_testkit_fixture() -> EventBridgeRepository:
    """Inicializa o MotoTestKit e retorna o repositório configurado."""
    moto_testkit = MotoTestKit(auto_start=True)
    repository = EventBridgeRepository(
        endpoint_url=moto_testkit.get_client("events").meta.endpoint_url
    )
    yield repository
    moto_testkit.stop()


def test_put_and_list_rules_with_fixture(
    moto_testkit_fixture: EventBridgeRepository,
) -> None:
    rule_name: str = "my-rule"
    moto_testkit_fixture.put_rule(rule_name, '{"source": ["app.test"]}')
    rules = moto_testkit_fixture.list_rules()
    assert rule_name in rules

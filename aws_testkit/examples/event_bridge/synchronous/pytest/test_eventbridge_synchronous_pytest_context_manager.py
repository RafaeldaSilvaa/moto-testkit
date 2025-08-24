import pytest

from aws_testkit.examples.event_bridge.synchronous.eventbridge_repository import EventBridgeRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit


def test_put_and_list_rules_with_context_manager() -> None:
    with AutoMotoTestKit(auto_start=True) as moto_testkit:
        repository = EventBridgeRepository(
            endpoint_url=moto_testkit.get_client("events").meta.endpoint_url
        )
        rule_name: str = "my-rule"

        repository.put_rule(rule_name, '{"source": ["app.test"]}')
        rules = repository.list_rules()

        assert rule_name in rules

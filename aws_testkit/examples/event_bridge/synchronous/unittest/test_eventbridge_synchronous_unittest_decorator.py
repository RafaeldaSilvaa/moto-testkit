import unittest

from aws_testkit.examples.event_bridge.synchronous.eventbridge_synchronous_repository import \
    EventBridgeRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit, use_moto_testkit


class TestEventBridgeRepositoryWithDecorator(unittest.TestCase):
    @use_moto_testkit(
        auto_start=True,
    )
    def test_put_and_list_rules(self, moto_testkit: AutoMotoTestKit) -> None:
        repository: EventBridgeRepository = EventBridgeRepository(
            endpoint_url=moto_testkit.get_client("events").meta.endpoint_url
        )
        rule_name: str = "my-rule"

        repository.put_rule(rule_name, '{"source": ["app.test"]}')
        rules = repository.list_rules()
        self.assertIn(rule_name, rules)

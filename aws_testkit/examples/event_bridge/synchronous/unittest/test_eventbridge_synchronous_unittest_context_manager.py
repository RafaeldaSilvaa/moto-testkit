import unittest

from aws_testkit.examples.event_bridge.synchronous.eventbridge_synchronous_repository import \
    EventBridgeRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestEventBridgeRepositoryWithContextManager(unittest.TestCase):
    def test_put_and_list_rules(self) -> None:
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=False) as moto_testkit:
            repository: EventBridgeRepository = EventBridgeRepository(
                endpoint_url=moto_testkit.get_client("events").meta.endpoint_url
            )
            rule_name: str = "my-rule"

            repository.put_rule(rule_name, '{"source": ["app.test"]}')
            rules = repository.list_rules()
            self.assertIn(rule_name, rules)

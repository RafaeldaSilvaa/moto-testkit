import unittest

from examples.event_bridge.synchronous.eventbridge_synchronous_repository import \
    EventBridgeRepository
from src import MotoTestKit


class TestEventBridgeRepositoryFixtureMotoTestKit(unittest.TestCase):
    def setUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(auto_start=True)
        self.repository: EventBridgeRepository = EventBridgeRepository(
            endpoint_url=self.moto_testkit.get_client("events").meta.endpoint_url
        )

    def tearDown(self) -> None:
        self.moto_testkit.stop()

    def test_put_and_list_rules(self) -> None:
        rule_name: str = "my-rule"
        self.repository.put_rule(rule_name, '{"source": ["app.test"]}')
        rules = self.repository.list_rules()
        self.assertIn(rule_name, rules)

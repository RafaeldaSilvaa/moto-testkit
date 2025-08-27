import unittest

from examples.event_bridge.asynchronous.eventbridge_asynchronous_repository import EventBridgeAsyncRepository
from src.moto_testkit import AutoMotoTestKit, use_moto_testkit


class TestEventBridgeRepositoryWithDecorator(unittest.IsolatedAsyncioTestCase):
    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_put_rule_and_list(self, moto_testkit: AutoMotoTestKit) -> None:
        repository: EventBridgeAsyncRepository = EventBridgeAsyncRepository()
        rule_name: str = "regra-teste"

        await repository.put_rule(rule_name, '{"source": ["app.test"]}')
        rules = await repository.list_rules()

        self.assertIn(rule_name, rules)

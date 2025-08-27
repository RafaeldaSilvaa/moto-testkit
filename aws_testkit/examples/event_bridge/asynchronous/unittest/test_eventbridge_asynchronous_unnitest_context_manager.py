import unittest
from aws_testkit.examples.event_bridge.asynchronous.eventbridge_asynchronous_repository import (
    EventBridgeAsyncRepository,
)
from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestEventBridgeRepositoryWithContextManager(unittest.IsolatedAsyncioTestCase):
    async def test_put_rule_and_list(self) -> None:
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
            repository: EventBridgeAsyncRepository = EventBridgeAsyncRepository()
            rule_name: str = "regra-teste"

            await repository.put_rule(rule_name, '{"source": ["app.test"]}')
            rules = await repository.list_rules()

            self.assertIn(rule_name, rules)

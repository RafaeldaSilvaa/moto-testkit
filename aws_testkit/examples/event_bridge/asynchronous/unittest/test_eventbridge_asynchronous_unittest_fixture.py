import unittest
from aws_testkit.src import MotoTestKit
from aws_testkit.examples.event_bridge.asynchronous.eventbridge_asynchronous_repository import (
    EventBridgeAsyncRepository,
)


class TestEventBridgeRepositoryFixtureMotoTestKit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        self.repository: EventBridgeAsyncRepository = EventBridgeAsyncRepository()

    async def asyncTearDown(self) -> None:
        await self.moto_testkit.close_async_clients()
        self.moto_testkit.stop()

    async def test_put_rule_and_list(self) -> None:
        rule_name: str = "regra-teste"
        await self.repository.put_rule(rule_name, '{"source": ["app.test"]}')
        rules = await self.repository.list_rules()
        self.assertIn(rule_name, rules)

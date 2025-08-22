import unittest

from aws_testkit.examples.event_bridge.assincrono.eventbridge_async_repository import EventBridgeAsyncRepository
from aws_testkit.src import MotoTestKit


class TestEventBridgeRepositoryWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        self.repo = EventBridgeAsyncRepository()

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_put_rule_and_list(self):
        await self.repo.put_rule("regra-teste", '{"source": ["app.test"]}')
        regras = await self.repo.list_rules()
        self.assertIn("regra-teste", regras)

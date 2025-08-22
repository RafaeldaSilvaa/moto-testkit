import unittest

from aws_testkit.src import MotoTestKit


class TestEventBridgeWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Inicia o MotoTestKit antes de cada teste
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    async def asyncTearDown(self):
        # Fecha e para o MotoTestKit automaticamente
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_eventbridge_put_rule_and_list(self):
        eb_client = await self.kit.get_async_client("events")

        rule_name = "minha-regra-teste"
        await eb_client.put_rule(
            Name=rule_name,
            ScheduleExpression="rate(5 minutes)"
        )

        resp = await eb_client.list_rules()
        rules = [r["Name"] for r in resp.get("Rules", [])]

        self.assertIn(rule_name, rules, f"A regra '{rule_name}' não foi encontrada.")

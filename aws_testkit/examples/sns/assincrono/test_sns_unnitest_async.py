import unittest

from aws_testkit.src import MotoTestKit


class TestSNSWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_sns_create_and_list_topics(self):
        sns_client = await self.kit.get_async_client("sns")

        topic_name = "meu-topico-teste"
        await sns_client.create_topic(Name=topic_name)

        resp = await sns_client.list_topics()
        topics = [t["TopicArn"] for t in resp.get("Topics", [])]

        self.assertTrue(
            any(topic_name in arn for arn in topics),
            f"O tópico '{topic_name}' não foi encontrado."
        )

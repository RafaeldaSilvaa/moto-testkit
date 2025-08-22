import unittest

from aws_testkit.examples.sns.assincrono.sns_async_repository import SNSAsyncRepository
from aws_testkit.src import MotoTestKit


class TestSNSRepositoryWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        self.repo = SNSAsyncRepository()

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_create_and_list_topics(self):
        arn = await self.repo.create_topic("topico-teste")
        topics = await self.repo.list_topics()
        self.assertIn(arn, topics)

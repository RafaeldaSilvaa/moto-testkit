import unittest

from examples.sns.asynchronous.sns_asynchronous_repository import SNSAsyncRepository
from src import MotoTestKit


class TestSNSRepositoryFixtureMotoTestKit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(
            auto_start=True, patch_aiobotocore=True
        )
        self.repository: SNSAsyncRepository = SNSAsyncRepository()

    async def asyncTearDown(self) -> None:
        await self.moto_testkit.close_async_clients()
        self.moto_testkit.stop()

    async def test_create_and_list_topics(self) -> None:
        arn = await self.repository.create_topic("topico-teste")
        topics = await self.repository.list_topics()
        self.assertIn(arn, topics)

import unittest
from aws_testkit.examples.sns.asynchronous.sns_asynchronous_repository import SNSAsyncRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestSNSRepositoryWithContextManager(unittest.IsolatedAsyncioTestCase):
    async def test_create_and_list_topics(self) -> None:
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
            repository = SNSAsyncRepository()
            arn = await repository.create_topic("topico-teste")
            topics = await repository.list_topics()
            self.assertIn(arn, topics)

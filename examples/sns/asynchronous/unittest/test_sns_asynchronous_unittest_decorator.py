import unittest

from examples.sns.asynchronous.sns_asynchronous_repository import \
    SNSAsyncRepository
from src.moto_testkit import AutoMotoTestKit, use_moto_testkit


class TestSNSRepositoryWithDecorator(unittest.IsolatedAsyncioTestCase):
    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_create_and_list_topics(self, moto_testkit: AutoMotoTestKit) -> None:
        repository = SNSAsyncRepository()
        arn = await repository.create_topic("topico-teste")
        topics = await repository.list_topics()
        self.assertIn(arn, topics)

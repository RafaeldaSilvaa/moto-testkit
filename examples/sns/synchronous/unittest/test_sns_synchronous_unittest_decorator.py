import unittest

from examples.sns.synchronous.sns_synchronous_repository import SNSRepository
from src.moto_testkit import AutoMotoTestKit, use_moto_testkit


class TestSNSRepositoryWithDecorator(unittest.TestCase):
    @use_moto_testkit(auto_start=True)
    def test_create_and_list_topics(self, moto_testkit: AutoMotoTestKit) -> None:
        repository = SNSRepository(
            endpoint_url=moto_testkit.get_client("sns").meta.endpoint_url
        )
        arn = repository.create_topic("my-topic")
        self.assertIn("my-topic", arn)
        self.assertIn(arn, repository.list_topics())

    @use_moto_testkit(auto_start=True)
    def test_publish_message(self, moto_testkit: AutoMotoTestKit) -> None:
        repository = SNSRepository(
            endpoint_url=moto_testkit.get_client("sns").meta.endpoint_url
        )
        arn = repository.create_topic("my-topic")
        resp = repository.publish(arn, "Hello SNS")
        self.assertIn("MessageId", resp)

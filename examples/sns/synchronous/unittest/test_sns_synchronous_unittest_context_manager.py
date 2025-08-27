import unittest

from examples.sns.synchronous.sns_synchronous_repository import SNSRepository
from src.moto_testkit import AutoMotoTestKit


class TestSNSRepositoryWithContextManager(unittest.TestCase):
    def test_create_and_list_topics(self) -> None:
        with AutoMotoTestKit(auto_start=True) as moto_testkit:
            repository = SNSRepository(
                endpoint_url=moto_testkit.get_client("sns").meta.endpoint_url
            )
            arn = repository.create_topic("my-topic")
            self.assertIn("my-topic", arn)
            self.assertIn(arn, repository.list_topics())

    def test_publish_message(self) -> None:
        with AutoMotoTestKit(auto_start=True) as moto_testkit:
            repository = SNSRepository(
                endpoint_url=moto_testkit.get_client("sns").meta.endpoint_url
            )
            arn = repository.create_topic("my-topic")
            resp = repository.publish(arn, "Hello SNS")
            self.assertIn("MessageId", resp)

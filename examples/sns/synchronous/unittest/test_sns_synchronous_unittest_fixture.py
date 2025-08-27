import unittest

from examples.sns.synchronous.sns_synchronous_repository import \
    SNSRepository
from src import MotoTestKit


class TestSNSRepositoryFixtureMotoTestKit(unittest.TestCase):
    def setUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(auto_start=True)
        self.repository: SNSRepository = SNSRepository(
            endpoint_url=self.moto_testkit.get_client("sns").meta.endpoint_url
        )

    def tearDown(self) -> None:
        self.moto_testkit.stop()

    def test_create_and_list_topics(self) -> None:
        arn = self.repository.create_topic("my-topic")
        self.assertIn("my-topic", arn)
        self.assertIn(arn, self.repository.list_topics())

    def test_publish_message(self) -> None:
        arn = self.repository.create_topic("my-topic")
        resp = self.repository.publish(arn, "Hello SNS")
        self.assertIn("MessageId", resp)

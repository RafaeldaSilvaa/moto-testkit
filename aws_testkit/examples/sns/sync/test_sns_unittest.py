import unittest
from aws_testkit.src import MotoTestKit
from sns_repository import SNSRepository

class TestSNSRepository(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True)
        self.repo = SNSRepository(endpoint_url=self.kit.get_client("sns").meta.endpoint_url)

    def tearDown(self):
        self.kit.stop()

    def test_create_and_list_topics(self):
        arn = self.repo.create_topic("my-topic")
        self.assertIn("my-topic", arn)
        topics = self.repo.list_topics()
        self.assertIn(arn, topics)

    def test_publish_message(self):
        arn = self.repo.create_topic("my-topic")
        resp = self.repo.publish(arn, "Hello SNS")
        self.assertIn("MessageId", resp)

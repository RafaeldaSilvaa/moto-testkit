# test_sqs_unittest.py
import unittest
from aws_testkit.src import MotoTestKit
from sqs_repository import SQSRepository


class TestSQSRepository(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True)
        self.repo = SQSRepository(endpoint_url=self.kit.get_client("sqs").meta.endpoint_url)
        self.queue_url = self.repo.create_queue("test-queue")

    def tearDown(self):
        self.kit.stop()

    def test_send_and_receive_message(self):
        self.repo.send_message(self.queue_url, "Hello")
        messages = self.repo.receive_messages(self.queue_url)
        self.assertEqual(messages[0]["Body"], "Hello")

    def test_delete_message(self):
        self.repo.send_message(self.queue_url, "Bye")
        messages = self.repo.receive_messages(self.queue_url)
        receipt_handle = messages[0]["ReceiptHandle"]
        self.repo.delete_message(self.queue_url, receipt_handle)
        messages_after = self.repo.receive_messages(self.queue_url)
        self.assertEqual(messages_after, [])

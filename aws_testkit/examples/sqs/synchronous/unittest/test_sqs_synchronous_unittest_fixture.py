import unittest

from aws_testkit.examples.sqs.synchronous.sqs_synchronous_repository import \
    SQSRepository
from aws_testkit.src import MotoTestKit


class TestSQSRepositoryFixtureMotoTestKit(unittest.TestCase):
    def setUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(auto_start=True)
        self.repository: SQSRepository = SQSRepository(
            endpoint_url=self.moto_testkit.get_client("sqs").meta.endpoint_url
        )
        self.queue_url: str = self.repository.create_queue("test-queue")

    def tearDown(self) -> None:
        self.moto_testkit.stop()

    def test_send_and_receive_message(self) -> None:
        self.repository.send_message(self.queue_url, "Hello")
        messages = self.repository.receive_messages(self.queue_url)
        self.assertEqual(messages[0]["Body"], "Hello")

    def test_delete_message(self) -> None:
        self.repository.send_message(self.queue_url, "Bye")
        messages = self.repository.receive_messages(self.queue_url)
        receipt_handle = messages[0]["ReceiptHandle"]
        self.repository.delete_message(self.queue_url, receipt_handle)
        self.assertEqual(self.repository.receive_messages(self.queue_url), [])

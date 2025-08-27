import unittest

from aws_testkit.examples.sqs.synchronous.sqs_synchronous_repository import SQSRepository
from aws_testkit.src.moto_testkit import use_moto_testkit, AutoMotoTestKit


class TestSQSRepositoryWithDecorator(unittest.TestCase):
    @use_moto_testkit(auto_start=True)
    def test_send_and_receive_message(self, moto_testkit: AutoMotoTestKit) -> None:
        repository = SQSRepository(endpoint_url=moto_testkit.get_client("sqs").meta.endpoint_url)
        queue_url = repository.create_queue("test-queue")
        repository.send_message(queue_url, "Hello")
        messages = repository.receive_messages(queue_url)
        self.assertEqual(messages[0]["Body"], "Hello")

    @use_moto_testkit(auto_start=True)
    def test_delete_message(self, moto_testkit: AutoMotoTestKit) -> None:
        repository = SQSRepository(endpoint_url=moto_testkit.get_client("sqs").meta.endpoint_url)
        queue_url = repository.create_queue("test-queue")
        repository.send_message(queue_url, "Bye")
        messages = repository.receive_messages(queue_url)
        receipt_handle = messages[0]["ReceiptHandle"]
        repository.delete_message(queue_url, receipt_handle)
        self.assertEqual(repository.receive_messages(queue_url), [])

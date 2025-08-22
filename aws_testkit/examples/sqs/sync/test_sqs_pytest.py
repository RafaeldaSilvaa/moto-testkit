# test_sqs_pytest.py
import pytest
from aws_testkit.src import MotoTestKit
from sqs_repository import SQSRepository


@pytest.fixture
def repo():
    kit = MotoTestKit(auto_start=True)
    repo = SQSRepository(endpoint_url=kit.get_client("sqs").meta.endpoint_url)
    queue_url = repo.create_queue("test-queue")
    yield repo, queue_url
    kit.stop()


def test_send_and_receive_message(repo):
    sqs_repo, queue_url = repo
    sqs_repo.send_message(queue_url, "Hello")
    messages = sqs_repo.receive_messages(queue_url)
    assert messages[0]["Body"] == "Hello"


def test_delete_message(repo):
    sqs_repo, queue_url = repo
    sqs_repo.send_message(queue_url, "Bye")
    messages = sqs_repo.receive_messages(queue_url)
    receipt_handle = messages[0]["ReceiptHandle"]
    sqs_repo.delete_message(queue_url, receipt_handle)
    messages_after = sqs_repo.receive_messages(queue_url)
    assert messages_after == []

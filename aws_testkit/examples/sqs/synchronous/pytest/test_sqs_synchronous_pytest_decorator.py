from aws_testkit.examples.sqs.synchronous.sqs_synchronous_repository import \
    SQSRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit, use_moto_testkit


@use_moto_testkit(auto_start=True)
def test_send_and_receive_message_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository = SQSRepository(
        endpoint_url=moto_testkit.get_client("sqs").meta.endpoint_url
    )
    queue_url = repository.create_queue("test-queue")
    repository.send_message(queue_url, "Hello")
    messages = repository.receive_messages(queue_url)
    assert messages[0]["Body"] == "Hello"


@use_moto_testkit(auto_start=True)
def test_delete_message_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository = SQSRepository(
        endpoint_url=moto_testkit.get_client("sqs").meta.endpoint_url
    )
    queue_url = repository.create_queue("test-queue")
    repository.send_message(queue_url, "Bye")
    messages = repository.receive_messages(queue_url)
    receipt_handle = messages[0]["ReceiptHandle"]
    repository.delete_message(queue_url, receipt_handle)
    assert repository.receive_messages(queue_url) == []

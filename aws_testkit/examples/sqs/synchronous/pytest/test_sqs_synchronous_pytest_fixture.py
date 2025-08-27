import pytest

from aws_testkit.examples.sqs.synchronous.sqs_synchronous_repository import \
    SQSRepository
from aws_testkit.src import MotoTestKit


@pytest.fixture
def moto_testkit_fixture() -> tuple[SQSRepository, str]:
    """Inicializa MotoTestKit e retorna repositório SQS e URL da fila."""
    moto_testkit = MotoTestKit(auto_start=True)
    repository = SQSRepository(
        endpoint_url=moto_testkit.get_client("sqs").meta.endpoint_url
    )
    queue_url = repository.create_queue("test-queue")
    yield repository, queue_url
    moto_testkit.stop()


def test_send_and_receive_message_with_fixture(
    moto_testkit_fixture: tuple[SQSRepository, str]
) -> None:
    repo, queue_url = moto_testkit_fixture
    repo.send_message(queue_url, "Hello")
    messages = repo.receive_messages(queue_url)
    assert messages[0]["Body"] == "Hello"


def test_delete_message_with_fixture(
    moto_testkit_fixture: tuple[SQSRepository, str]
) -> None:
    repo, queue_url = moto_testkit_fixture
    repo.send_message(queue_url, "Bye")
    messages = repo.receive_messages(queue_url)
    receipt_handle = messages[0]["ReceiptHandle"]
    repo.delete_message(queue_url, receipt_handle)
    assert repo.receive_messages(queue_url) == []

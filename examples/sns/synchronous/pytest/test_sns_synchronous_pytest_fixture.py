import pytest

from examples.sns.synchronous.sns_synchronous_repository import \
    SNSRepository
from src import MotoTestKit


@pytest.fixture
def moto_testkit_fixture() -> SNSRepository:
    """Inicializa MotoTestKit e retorna repositório SNS configurado."""
    moto_testkit = MotoTestKit(auto_start=True)
    repository = SNSRepository(
        endpoint_url=moto_testkit.get_client("sns").meta.endpoint_url
    )
    yield repository
    moto_testkit.stop()


def test_create_and_list_topics_with_fixture(
    moto_testkit_fixture: SNSRepository,
) -> None:
    arn = moto_testkit_fixture.create_topic("my-topic")
    assert "my-topic" in arn
    assert arn in moto_testkit_fixture.list_topics()


def test_publish_message_with_fixture(moto_testkit_fixture: SNSRepository) -> None:
    arn = moto_testkit_fixture.create_topic("my-topic")
    resp = moto_testkit_fixture.publish(arn, "Hello SNS")
    assert "MessageId" in resp

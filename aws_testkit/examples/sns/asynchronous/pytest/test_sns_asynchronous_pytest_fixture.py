import pytest
import pytest_asyncio

from aws_testkit.examples.sns.asynchronous.sns_asynchronous_repository import \
    SNSAsyncRepository
from aws_testkit.src import MotoTestKit


@pytest_asyncio.fixture
async def moto_testkit_fixture() -> MotoTestKit:
    """Inicializa MotoTestKit assíncrono para testes com SNS."""
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    await kit.close_async_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_sns_create_and_list_topics_with_fixture(
    moto_testkit_fixture: MotoTestKit,
) -> None:
    repository = SNSAsyncRepository()
    arn = await repository.create_topic("topico-teste")
    topics = await repository.list_topics()
    assert arn in topics

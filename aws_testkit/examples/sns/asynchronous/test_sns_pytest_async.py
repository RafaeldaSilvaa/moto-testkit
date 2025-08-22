import pytest_asyncio
import pytest

from aws_testkit.examples.sns.asynchronous.sns_async_repository import SNSAsyncRepository
from aws_testkit.src import MotoTestKit


@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    await kit.close_async_clients()
    kit.stop()

@pytest.mark.asyncio
async def test_sns_create_and_list_topics(moto_kit):
    repo = SNSAsyncRepository()
    arn = await repo.create_topic("topico-teste")
    topics = await repo.list_topics()
    assert arn in topics

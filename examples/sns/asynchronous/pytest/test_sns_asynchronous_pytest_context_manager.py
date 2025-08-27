import pytest

from examples.sns.asynchronous.sns_asynchronous_repository import SNSAsyncRepository
from src.moto_testkit import AutoMotoTestKit


@pytest.mark.asyncio
async def test_sns_create_and_list_topics_with_context_manager() -> None:
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
        repository = SNSAsyncRepository()
        arn = await repository.create_topic("topico-teste")
        topics = await repository.list_topics()
        assert arn in topics

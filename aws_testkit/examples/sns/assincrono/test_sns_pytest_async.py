import pytest_asyncio
import pytest

from aws_testkit.src import MotoTestKit


@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    await kit.close_async_clients()
    kit.stop()

@pytest.mark.asyncio
async def test_sns_publish_and_list(moto_kit):
    sns_client = await moto_kit.get_async_client("sns")

    topic_arn = (await sns_client.create_topic(Name="meu-topico"))["TopicArn"]
    await sns_client.publish(TopicArn=topic_arn, Message="Olá SNS!")

    topics = await sns_client.list_topics()
    arns = [t["TopicArn"] for t in topics.get("Topics", [])]

    assert topic_arn in arns

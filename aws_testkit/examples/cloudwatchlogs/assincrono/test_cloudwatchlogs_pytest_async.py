import pytest
import pytest_asyncio

from aws_testkit.src import MotoTestKit

@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    kit.close_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_cloudwatchlogs_create_and_list(moto_kit):
    logs_client = await moto_kit.get_async_client("logs")

    group_name = "meu-grupo-logs"
    await logs_client.create_log_group(logGroupName=group_name)

    resp = await logs_client.describe_log_groups()
    nomes = [g["logGroupName"] for g in resp.get("logGroups", [])]

    assert group_name in nomes

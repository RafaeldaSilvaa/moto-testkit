import pytest
import pytest_asyncio
from typing import AsyncGenerator, List, Dict, Any

from aws_testkit.examples.cloudwatchlogs.asynchronous.cloudwatchlogs_asynchronous_repository import (
    CloudWatchLogsAsyncRepository,
)
from aws_testkit.src import MotoTestKit


@pytest_asyncio.fixture
async def moto_testkit() -> AsyncGenerator[MotoTestKit, None]:
    """Fixture to initialize and yield a MotoTestKit instance for AWS mocking."""
    testkit_instance = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield testkit_instance
    testkit_instance.close_clients()
    testkit_instance.stop()


@pytest.mark.asyncio
async def test_create_log_group_and_describe(moto_testkit: MotoTestKit) -> None:
    """
    Create a log group and verify it appears in the list of log groups.
    """
    endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
    logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    # Act: create log group
    await logs_repo.create_log_group("grupo-logs-fixture")
    log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()

    # Assert
    assert "grupo-logs-fixture" in [g["logGroupName"] for g in log_groups]


@pytest.mark.asyncio
async def test_create_log_stream(moto_testkit: MotoTestKit) -> None:
    """
    Create a log group, then create a log stream inside it, and verify.
    """
    endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
    logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    await logs_repo.create_log_group("grupo-stream-fixture")
    await logs_repo.create_log_stream("grupo-stream-fixture", "stream-fixture")

    logs_client = await moto_testkit.get_async_client("logs")
    resp = await logs_client.describe_log_streams(logGroupName="grupo-stream-fixture")
    assert "stream-fixture" in [s["logStreamName"] for s in resp.get("logStreams", [])]


@pytest.mark.asyncio
async def test_put_log_events(moto_testkit: MotoTestKit) -> None:
    """
    Create a log group and stream, put log events, and confirm sequence token is returned.
    """
    endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
    logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    await logs_repo.create_log_group("grupo-logs-eventos-fixture")
    await logs_repo.create_log_stream("grupo-logs-eventos-fixture", "stream-eventos-fixture")
    resp = await logs_repo.put_log_events(
        "grupo-logs-eventos-fixture",
        "stream-eventos-fixture",
        ["mensagem 1", "mensagem 2"],
    )
    assert "nextSequenceToken" in resp


@pytest.mark.asyncio
async def test_full_flow(moto_testkit: MotoTestKit) -> None:
    """
    Run full flow: create group, create stream, put events, and verify in group list.
    """
    endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
    logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    log_group_name = "grupo-completo-fixture"
    log_stream_name = "stream-completo-fixture"

    await logs_repo.create_log_group(log_group_name)
    await logs_repo.create_log_stream(log_group_name, log_stream_name)
    await logs_repo.put_log_events(log_group_name, log_stream_name, ["log 1", "log 2"])

    log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
    assert log_group_name in [g["logGroupName"] for g in log_groups]

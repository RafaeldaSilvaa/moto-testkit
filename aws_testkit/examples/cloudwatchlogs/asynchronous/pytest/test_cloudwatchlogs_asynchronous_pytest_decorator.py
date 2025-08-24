import pytest
from typing import List, Dict, Any

from aws_testkit.examples.cloudwatchlogs.asynchronous.cloudwatchlogs_asynchronous_repository import (
    CloudWatchLogsAsyncRepository,
)
from aws_testkit.src import MotoTestKit
from aws_testkit.src.moto_testkit import use_moto_testkit


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_create_log_group_and_describe(moto_testkit: MotoTestKit) -> None:
    """
    Create a CloudWatch Logs group and verify it appears in the list of log groups.
    """
    endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
    logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    # Act: create log group
    await logs_repo.create_log_group("grupo-logs-decorator")
    log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()

    # Assert
    assert "grupo-logs-decorator" in [g["logGroupName"] for g in log_groups]


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_create_log_stream(moto_testkit: MotoTestKit) -> None:
    """
    Create a CloudWatch Logs group, then a log stream inside it, and verify.
    """
    endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
    logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    # Arrange: create log group
    await logs_repo.create_log_group("grupo-stream-decorator")

    # Act: create log stream
    await logs_repo.create_log_stream("grupo-stream-decorator", "stream-decorator")

    # Assert using direct client
    logs_client = await moto_testkit.get_async_client("logs")
    resp = await logs_client.describe_log_streams(logGroupName="grupo-stream-decorator")
    assert "stream-decorator" in [s["logStreamName"] for s in resp.get("logStreams", [])]


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_put_log_events(moto_testkit: MotoTestKit) -> None:
    """
    Create a log group and stream, put log events, and confirm that a sequence token is returned.
    """
    endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
    logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    # Arrange
    await logs_repo.create_log_group("grupo-logs-eventos-decorator")
    await logs_repo.create_log_stream("grupo-logs-eventos-decorator", "stream-eventos-decorator")

    # Act
    resp = await logs_repo.put_log_events(
        "grupo-logs-eventos-decorator",
        "stream-eventos-decorator",
        ["mensagem 1", "mensagem 2"],
    )

    # Assert
    assert "nextSequenceToken" in resp


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_full_flow(moto_testkit: MotoTestKit) -> None:
    """
    Test the full CloudWatch Logs flow:
    - Create log group
    - Create log stream
    - Put log events
    - Verify group in list
    """
    endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
    logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    log_group_name = "grupo-completo-decorator"
    log_stream_name = "stream-completo-decorator"

    # Create group and stream, then put events
    await logs_repo.create_log_group(log_group_name)
    await logs_repo.create_log_stream(log_group_name, log_stream_name)
    await logs_repo.put_log_events(log_group_name, log_stream_name, ["log 1", "log 2"])

    # Assert group exists
    log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
    assert log_group_name in [g["logGroupName"] for g in log_groups]

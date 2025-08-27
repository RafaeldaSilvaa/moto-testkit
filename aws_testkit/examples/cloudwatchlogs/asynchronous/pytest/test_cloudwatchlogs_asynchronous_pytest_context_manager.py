from typing import Any, Dict, List

import pytest

from aws_testkit.examples.cloudwatchlogs.asynchronous.cloudwatchlogs_asynchronous_repository import \
    CloudWatchLogsAsyncRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit


@pytest.mark.asyncio
async def test_create_log_group_and_describe() -> None:
    """
    Create a log group and verify it appears in the list of log groups.
    """
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-logs-with")
        log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
        assert "grupo-logs-with" in [g["logGroupName"] for g in log_groups]


@pytest.mark.asyncio
async def test_create_log_stream() -> None:
    """
    Create a log group, then a stream, and verify.
    """
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-stream-with")
        await logs_repo.create_log_stream("grupo-stream-with", "stream-with")

        logs_client = await moto_testkit.get_async_client("logs")
        resp = await logs_client.describe_log_streams(logGroupName="grupo-stream-with")
        assert "stream-with" in [s["logStreamName"] for s in resp.get("logStreams", [])]


@pytest.mark.asyncio
async def test_put_log_events() -> None:
    """
    Put log events into a newly created group and stream, verify sequence token.
    """
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-logs-eventos-with")
        await logs_repo.create_log_stream(
            "grupo-logs-eventos-with", "stream-eventos-with"
        )
        resp = await logs_repo.put_log_events(
            "grupo-logs-eventos-with",
            "stream-eventos-with",
            ["mensagem 1", "mensagem 2"],
        )
        assert "nextSequenceToken" in resp


@pytest.mark.asyncio
async def test_full_flow() -> None:
    """
    Full flow test using 'with' context manager for MotoTestKit.
    """
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        grupo = "grupo-completo-with"
        stream = "stream-completo-with"

        await logs_repo.create_log_group(grupo)
        await logs_repo.create_log_stream(grupo, stream)
        await logs_repo.put_log_events(grupo, stream, ["log 1", "log 2"])

        log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
        assert grupo in [g["logGroupName"] for g in log_groups]

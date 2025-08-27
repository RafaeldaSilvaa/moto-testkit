import unittest
from typing import Any, Dict, List

from aws_testkit.examples.cloudwatchlogs.asynchronous.cloudwatchlogs_asynchronous_repository import \
    CloudWatchLogsAsyncRepository
from aws_testkit.src import MotoTestKit
from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestCloudWatchLogsWithAutoMotoTestKit(unittest.IsolatedAsyncioTestCase):
    """Tests for CloudWatch Logs using unittest with 'with AutoMotoTestKit' pattern."""

    async def test_create_log_group_and_describe(self) -> None:
        """Create a log group and verify it appears."""
        async with AutoMotoTestKit(
            auto_start=True, patch_aiobotocore=True
        ) as moto_testkit:
            endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
            logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

            await logs_repo.create_log_group("grupo-logs-with")
            log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
            self.assertIn("grupo-logs-with", [g["logGroupName"] for g in log_groups])

    async def test_create_log_stream(self) -> None:
        """Create group, then stream, then verify."""
        async with AutoMotoTestKit(
            auto_start=True, patch_aiobotocore=True
        ) as moto_testkit:
            endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
            logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

            await logs_repo.create_log_group("grupo-stream-with")
            await logs_repo.create_log_stream("grupo-stream-with", "stream-with")

            logs_client = await moto_testkit.get_async_client("logs")
            resp = await logs_client.describe_log_streams(
                logGroupName="grupo-stream-with"
            )
            self.assertIn(
                "stream-with", [s["logStreamName"] for s in resp.get("logStreams", [])]
            )

    async def test_put_log_events(self) -> None:
        """Put events and verify sequence token."""
        async with AutoMotoTestKit(
            auto_start=True, patch_aiobotocore=True
        ) as moto_testkit:
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
            self.assertIn("nextSequenceToken", resp)

    async def test_full_flow(self) -> None:
        """Full flow: group → stream → events → verify."""
        async with AutoMotoTestKit(
            auto_start=True, patch_aiobotocore=True
        ) as moto_testkit:
            endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
            logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

            grupo = "grupo-completo-with"
            stream = "stream-completo-with"

            await logs_repo.create_log_group(grupo)
            await logs_repo.create_log_stream(grupo, stream)
            await logs_repo.put_log_events(grupo, stream, ["log 1", "log 2"])

            log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
            self.assertIn(grupo, [g["logGroupName"] for g in log_groups])

import unittest
from typing import Any, Dict, List

from examples.cloudwatchlogs.asynchronous.cloudwatchlogs_asynchronous_repository import CloudWatchLogsAsyncRepository
from src import MotoTestKit
from src.moto_testkit import use_moto_testkit


class TestCloudWatchLogsDecoratorPerMethod(unittest.IsolatedAsyncioTestCase):
    """Tests for CloudWatch Logs using @use_moto_testkit applied on each method."""

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_create_log_group_and_describe(
        self, moto_testkit: MotoTestKit
    ) -> None:
        """Create a log group and verify it appears in the list."""
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-logs-decorator-method")
        log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
        self.assertIn(
            "grupo-logs-decorator-method", [g["logGroupName"] for g in log_groups]
        )

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_create_log_stream(self, moto_testkit: MotoTestKit) -> None:
        """Create a group, then a stream, and verify."""
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-stream-decorator-method")
        await logs_repo.create_log_stream(
            "grupo-stream-decorator-method", "stream-decorator-method"
        )

        logs_client = await moto_testkit.get_async_client("logs")
        resp = await logs_client.describe_log_streams(
            logGroupName="grupo-stream-decorator-method"
        )
        self.assertIn(
            "stream-decorator-method",
            [s["logStreamName"] for s in resp.get("logStreams", [])],
        )

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_put_log_events(self, moto_testkit: MotoTestKit) -> None:
        """Put events into a stream and verify a sequence token is returned."""
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-logs-eventos-decorator-method")
        await logs_repo.create_log_stream(
            "grupo-logs-eventos-decorator-method", "stream-eventos-decorator-method"
        )

        resp = await logs_repo.put_log_events(
            "grupo-logs-eventos-decorator-method",
            "stream-eventos-decorator-method",
            ["mensagem 1", "mensagem 2"],
        )

        self.assertIn("nextSequenceToken", resp)

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_full_flow(self, moto_testkit: MotoTestKit) -> None:
        """Full flow: group → stream → events → verify."""
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        grupo = "grupo-completo-decorator-method"
        stream = "stream-completo-decorator-method"

        await logs_repo.create_log_group(grupo)
        await logs_repo.create_log_stream(grupo, stream)
        await logs_repo.put_log_events(grupo, stream, ["log 1", "log 2"])

        log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
        self.assertIn(grupo, [g["logGroupName"] for g in log_groups])


@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
class TestCloudWatchLogsDecoratorOnClass(unittest.IsolatedAsyncioTestCase):
    """Tests for CloudWatch Logs using @use_moto_testkit applied at class level."""

    async def test_create_log_group_and_describe(
        self, moto_testkit: MotoTestKit
    ) -> None:
        """Create a log group and verify it appears in the list."""
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-logs-decorator-class")
        log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
        self.assertIn(
            "grupo-logs-decorator-class", [g["logGroupName"] for g in log_groups]
        )

    async def test_create_log_stream(self, moto_testkit: MotoTestKit) -> None:
        """Create group, then stream, then verify."""
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-stream-decorator-class")
        await logs_repo.create_log_stream(
            "grupo-stream-decorator-class", "stream-decorator-class"
        )

        logs_client = await moto_testkit.get_async_client("logs")
        resp = await logs_client.describe_log_streams(
            logGroupName="grupo-stream-decorator-class"
        )
        self.assertIn(
            "stream-decorator-class",
            [s["logStreamName"] for s in resp.get("logStreams", [])],
        )

    async def test_put_log_events(self, moto_testkit: MotoTestKit) -> None:
        """Put events and verify sequence token."""
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-logs-eventos-decorator-class")
        await logs_repo.create_log_stream(
            "grupo-logs-eventos-decorator-class", "stream-eventos-decorator-class"
        )

        resp = await logs_repo.put_log_events(
            "grupo-logs-eventos-decorator-class",
            "stream-eventos-decorator-class",
            ["mensagem 1", "mensagem 2"],
        )

        self.assertIn("nextSequenceToken", resp)

    async def test_full_flow(self, moto_testkit: MotoTestKit) -> None:
        """Full flow with decorator at class level."""
        endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        grupo = "grupo-completo-decorator-class"
        stream = "stream-completo-decorator-class"

        await logs_repo.create_log_group(grupo)
        await logs_repo.create_log_stream(grupo, stream)
        await logs_repo.put_log_events(grupo, stream, ["log 1", "log 2"])

        log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
        self.assertIn(grupo, [g["logGroupName"] for g in log_groups])

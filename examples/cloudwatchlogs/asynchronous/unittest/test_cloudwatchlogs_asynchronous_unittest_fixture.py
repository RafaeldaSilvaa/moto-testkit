import unittest
from typing import Any, Dict, List

from examples.cloudwatchlogs.asynchronous.cloudwatchlogs_asynchronous_repository import CloudWatchLogsAsyncRepository
from src import MotoTestKit


class TestCloudWatchLogsFixtureMotoTestKit(unittest.IsolatedAsyncioTestCase):
    """Tests for CloudWatch Logs using unittest with fixture-like setup/teardown."""

    def setUp(self) -> None:
        self.moto_testkit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    def tearDown(self) -> None:
        self.moto_testkit.close_clients()
        self.moto_testkit.stop()

    async def test_create_log_group_and_describe(self) -> None:
        """Create a log group and verify it appears in the list of log groups."""
        endpoint_url: str = self.moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-logs-fixture")
        log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()

        self.assertIn("grupo-logs-fixture", [g["logGroupName"] for g in log_groups])

    async def test_create_log_stream(self) -> None:
        """Create a log group, then a log stream inside it, and verify."""
        endpoint_url: str = self.moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-stream-fixture")
        await logs_repo.create_log_stream("grupo-stream-fixture", "stream-fixture")

        logs_client = await self.moto_testkit.get_async_client("logs")
        resp = await logs_client.describe_log_streams(
            logGroupName="grupo-stream-fixture"
        )

        self.assertIn(
            "stream-fixture", [s["logStreamName"] for s in resp.get("logStreams", [])]
        )

    async def test_put_log_events(self) -> None:
        """Create a log group and stream, put events, verify sequence token."""
        endpoint_url: str = self.moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        await logs_repo.create_log_group("grupo-logs-eventos-fixture")
        await logs_repo.create_log_stream(
            "grupo-logs-eventos-fixture", "stream-eventos-fixture"
        )

        resp = await logs_repo.put_log_events(
            "grupo-logs-eventos-fixture",
            "stream-eventos-fixture",
            ["mensagem 1", "mensagem 2"],
        )

        self.assertIn("nextSequenceToken", resp)

    async def test_full_flow(self) -> None:
        """Full lifecycle: group → stream → events → verify."""
        endpoint_url: str = self.moto_testkit.get_client("logs").meta.endpoint_url
        logs_repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

        grupo = "grupo-completo-fixture"
        stream = "stream-completo-fixture"

        await logs_repo.create_log_group(grupo)
        await logs_repo.create_log_stream(grupo, stream)
        await logs_repo.put_log_events(grupo, stream, ["log 1", "log 2"])

        log_groups: List[Dict[str, Any]] = await logs_repo.describe_log_groups()
        self.assertIn(grupo, [g["logGroupName"] for g in log_groups])

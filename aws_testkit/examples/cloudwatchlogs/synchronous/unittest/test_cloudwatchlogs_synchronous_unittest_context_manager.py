import unittest
from typing import List, Dict, Any

from aws_testkit.examples.cloudwatchlogs.synchronous.cloudwatchlogs_synchronous_repository import (
    CloudWatchLogsRepository,
)
from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestCloudWatchLogsRepositoryWithContextManager(unittest.TestCase):
    """Tests for CloudWatchLogsRepository using MotoTestKit as a context manager."""

    def test_create_group_and_stream(self) -> None:
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=False) as kit:
            repo = CloudWatchLogsRepository(endpoint_url=kit.get_client("logs").meta.endpoint_url)
            repo.create_log_group("my-group")
            repo.create_log_stream("my-group", "my-stream")
            groups: List[Dict[str, Any]] = repo.describe_log_groups()
            self.assertTrue(any(g["logGroupName"] == "my-group" for g in groups))

    def test_put_log_events(self) -> None:
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=False) as kit:
            repo = CloudWatchLogsRepository(endpoint_url=kit.get_client("logs").meta.endpoint_url)
            repo.create_log_group("my-group")
            repo.create_log_stream("my-group", "my-stream")
            resp: Dict[str, Any] = repo.put_log_events("my-group", "my-stream", ["msg1", "msg2"])
            self.assertIn("nextSequenceToken", resp)

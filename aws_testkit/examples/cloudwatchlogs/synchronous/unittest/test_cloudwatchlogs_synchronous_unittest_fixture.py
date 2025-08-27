import unittest
from typing import Any, Dict, List

from aws_testkit.examples.cloudwatchlogs.synchronous.cloudwatchlogs_synchronous_repository import \
    CloudWatchLogsRepository
from aws_testkit.src import MotoTestKit


class TestCloudWatchLogsRepositoryWithFixture(unittest.TestCase):
    """Tests for CloudWatchLogsRepository using setUp/tearDown fixture pattern."""

    def setUp(self) -> None:
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=False)
        self.repo = CloudWatchLogsRepository(
            endpoint_url=self.kit.get_client("logs").meta.endpoint_url
        )

    def tearDown(self) -> None:
        self.kit.stop()

    def test_create_group_and_stream(self) -> None:
        """Should create a log group and stream successfully."""
        self.repo.create_log_group("my-group")
        self.repo.create_log_stream("my-group", "my-stream")
        groups: List[Dict[str, Any]] = self.repo.describe_log_groups()
        self.assertTrue(any(g["logGroupName"] == "my-group" for g in groups))

    def test_put_log_events(self) -> None:
        """Should return a sequence token when log events are put."""
        self.repo.create_log_group("my-group")
        self.repo.create_log_stream("my-group", "my-stream")
        resp: Dict[str, Any] = self.repo.put_log_events(
            "my-group", "my-stream", ["msg1", "msg2"]
        )
        self.assertIn("nextSequenceToken", resp)

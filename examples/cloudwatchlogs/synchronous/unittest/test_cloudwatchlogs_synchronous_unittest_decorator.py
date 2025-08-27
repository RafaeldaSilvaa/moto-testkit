import unittest
from typing import Any, Dict, List

from examples.cloudwatchlogs.synchronous.cloudwatchlogs_synchronous_repository import CloudWatchLogsRepository
from src.moto_testkit import use_moto_testkit


@use_moto_testkit(auto_start=True, patch_aiobotocore=False)
class TestCloudWatchLogsRepositoryDecoratorOnClass(unittest.TestCase):
    """Tests with @use_moto_testkit applied at the class level."""

    def test_create_group_and_stream(self, moto_testkit) -> None:
        repo = CloudWatchLogsRepository(
            endpoint_url=moto_testkit.get_client("logs").meta.endpoint_url
        )
        repo.create_log_group("my-group")
        repo.create_log_stream("my-group", "my-stream")
        groups: List[Dict[str, Any]] = repo.describe_log_groups()
        self.assertTrue(any(g["logGroupName"] == "my-group" for g in groups))

    def test_put_log_events(self, moto_testkit) -> None:
        repo = CloudWatchLogsRepository(
            endpoint_url=moto_testkit.get_client("logs").meta.endpoint_url
        )
        repo.create_log_group("my-group")
        repo.create_log_stream("my-group", "my-stream")
        resp: Dict[str, Any] = repo.put_log_events(
            "my-group", "my-stream", ["msg1", "msg2"]
        )
        self.assertIn("nextSequenceToken", resp)


class TestCloudWatchLogsRepositoryDecoratorOnMethods(unittest.TestCase):
    """Tests with @use_moto_testkit applied on each test method."""

    @use_moto_testkit(auto_start=True, patch_aiobotocore=False)
    def test_create_group_and_stream(self, moto_testkit) -> None:
        repo = CloudWatchLogsRepository(
            endpoint_url=moto_testkit.get_client("logs").meta.endpoint_url
        )
        repo.create_log_group("my-group")
        repo.create_log_stream("my-group", "my-stream")
        groups: List[Dict[str, Any]] = repo.describe_log_groups()
        self.assertTrue(any(g["logGroupName"] == "my-group" for g in groups))

    @use_moto_testkit(auto_start=True, patch_aiobotocore=False)
    def test_put_log_events(self, moto_testkit) -> None:
        repo = CloudWatchLogsRepository(
            endpoint_url=moto_testkit.get_client("logs").meta.endpoint_url
        )
        repo.create_log_group("my-group")
        repo.create_log_stream("my-group", "my-stream")
        resp: Dict[str, Any] = repo.put_log_events(
            "my-group", "my-stream", ["msg1", "msg2"]
        )
        self.assertIn("nextSequenceToken", resp)

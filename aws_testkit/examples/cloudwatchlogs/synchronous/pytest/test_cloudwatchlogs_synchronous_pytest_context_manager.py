from typing import Any, Dict, List

from aws_testkit.examples.cloudwatchlogs.synchronous.cloudwatchlogs_synchronous_repository import \
    CloudWatchLogsRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit


def test_create_group_and_stream_with_context_manager() -> None:
    """Create a log group and stream using MotoTestKit as context manager."""
    with AutoMotoTestKit(auto_start=True, patch_aiobotocore=False) as kit:
        repo = CloudWatchLogsRepository(
            endpoint_url=kit.get_client("logs").meta.endpoint_url
        )
        repo.create_log_group("my-group")
        repo.create_log_stream("my-group", "my-stream")
        groups: List[Dict[str, Any]] = repo.describe_log_groups()
        assert any(g["logGroupName"] == "my-group" for g in groups)


def test_put_log_events_with_context_manager() -> None:
    """Put log events using context manager style."""
    with AutoMotoTestKit(auto_start=True, patch_aiobotocore=False) as kit:
        repo = CloudWatchLogsRepository(
            endpoint_url=kit.get_client("logs").meta.endpoint_url
        )
        repo.create_log_group("my-group")
        repo.create_log_stream("my-group", "my-stream")
        resp: Dict[str, Any] = repo.put_log_events(
            "my-group", "my-stream", ["msg1", "msg2"]
        )
        assert "nextSequenceToken" in resp

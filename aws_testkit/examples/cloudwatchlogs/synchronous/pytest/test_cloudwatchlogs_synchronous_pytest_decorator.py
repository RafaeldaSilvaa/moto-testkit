from typing import List, Dict, Any

from aws_testkit.examples.cloudwatchlogs.synchronous.cloudwatchlogs_synchronous_repository import \
    CloudWatchLogsRepository
from aws_testkit.src.moto_testkit import use_moto_testkit


@use_moto_testkit(auto_start=True, patch_aiobotocore=False)
def test_create_group_and_stream_with_decorator(moto_testkit) -> None:
    """Create group and stream using decorator style."""
    repo = CloudWatchLogsRepository(endpoint_url=moto_testkit.get_client("logs").meta.endpoint_url)
    repo.create_log_group("my-group")
    repo.create_log_stream("my-group", "my-stream")
    groups: List[Dict[str, Any]] = repo.describe_log_groups()
    assert any(g["logGroupName"] == "my-group" for g in groups)


@use_moto_testkit(auto_start=True, patch_aiobotocore=False)
def test_put_log_events_with_decorator(moto_testkit) -> None:
    """Put log events using decorator style."""
    repo = CloudWatchLogsRepository(endpoint_url=moto_testkit.get_client("logs").meta.endpoint_url)
    repo.create_log_group("my-group")
    repo.create_log_stream("my-group", "my-stream")
    resp: Dict[str, Any] = repo.put_log_events(
        "my-group", "my-stream", ["msg1", "msg2"]
    )
    assert "nextSequenceToken" in resp

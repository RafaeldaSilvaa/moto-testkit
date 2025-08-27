from typing import Any, Dict, Generator, List

import pytest

from aws_testkit.examples.cloudwatchlogs.synchronous.cloudwatchlogs_synchronous_repository import \
    CloudWatchLogsRepository
from aws_testkit.src import MotoTestKit


@pytest.fixture
def moto_testkit() -> Generator[MotoTestKit, None, None]:
    """Starts and stops the MotoTestKit for CloudWatch Logs."""
    kit_instance = MotoTestKit(auto_start=True, patch_aiobotocore=False)
    yield kit_instance
    kit_instance.stop()


@pytest.fixture
def cloudwatch_logs_repo(
    moto_testkit: MotoTestKit,
) -> Generator[CloudWatchLogsRepository, None, None]:
    """Provides a CloudWatchLogsRepository configured with the MotoTestKit logs endpoint."""
    endpoint_url: str = moto_testkit.get_client("logs").meta.endpoint_url
    repo_instance = CloudWatchLogsRepository(endpoint_url=endpoint_url)
    yield repo_instance


def test_create_group_and_stream(
    cloudwatch_logs_repo: CloudWatchLogsRepository,
) -> None:
    """Validate creating a log group and stream."""
    cloudwatch_logs_repo.create_log_group("my-group")
    cloudwatch_logs_repo.create_log_stream("my-group", "my-stream")
    groups: List[Dict[str, Any]] = cloudwatch_logs_repo.describe_log_groups()
    assert any(g["logGroupName"] == "my-group" for g in groups)


def test_put_log_events(cloudwatch_logs_repo: CloudWatchLogsRepository) -> None:
    """Validate putting log events returns a sequence token."""
    cloudwatch_logs_repo.create_log_group("my-group")
    cloudwatch_logs_repo.create_log_stream("my-group", "my-stream")
    resp: Dict[str, Any] = cloudwatch_logs_repo.put_log_events(
        "my-group", "my-stream", ["msg1", "msg2"]
    )
    assert "nextSequenceToken" in resp

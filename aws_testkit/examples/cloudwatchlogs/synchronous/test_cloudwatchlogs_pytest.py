import pytest
from aws_testkit.src import MotoTestKit
from cloudwatchlogs_repository import CloudWatchLogsRepository


@pytest.fixture
def repo():
    kit = MotoTestKit(auto_start=True)
    repo = CloudWatchLogsRepository(endpoint_url=kit.get_client("logs").meta.endpoint_url)
    yield repo
    kit.stop()


def test_create_group_and_stream(repo):
    repo.create_log_group("my-group")
    repo.create_log_stream("my-group", "my-stream")
    groups = repo.describe_log_groups()
    assert any(g["logGroupName"] == "my-group" for g in groups)


def test_put_log_events(repo):
    repo.create_log_group("my-group")
    repo.create_log_stream("my-group", "my-stream")
    resp = repo.put_log_events("my-group", "my-stream", ["msg1", "msg2"])
    assert "nextSequenceToken" in resp

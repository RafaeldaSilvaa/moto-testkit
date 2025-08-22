import pytest
from aws_testkit.src import MotoTestKit
from sns_repository import SNSRepository

@pytest.fixture
def repo():
    kit = MotoTestKit(auto_start=True)
    repo = SNSRepository(endpoint_url=kit.get_client("sns").meta.endpoint_url)
    yield repo
    kit.stop()

def test_create_and_list_topics(repo):
    arn = repo.create_topic("my-topic")
    assert "my-topic" in arn
    assert arn in repo.list_topics()

def test_publish_message(repo):
    arn = repo.create_topic("my-topic")
    resp = repo.publish(arn, "Hello SNS")
    assert "MessageId" in resp

import pytest
from aws_testkit.src import MotoTestKit
from eventbridge_repository import EventBridgeRepository

@pytest.fixture
def repo():
    kit = MotoTestKit(auto_start=True)
    repo = EventBridgeRepository(endpoint_url=kit.get_client("events").meta.endpoint_url)
    yield repo
    kit.stop()

def test_put_and_list_rules(repo):
    repo.put_rule("my-rule", '{"source": ["app.test"]}')
    assert "my-rule" in repo.list_rules()

import pytest
from aws_testkit.src import MotoTestKit
from iam_repository import IAMRepository

@pytest.fixture
def repo():
    kit = MotoTestKit(auto_start=True)
    repo = IAMRepository(endpoint_url=kit.get_client("iam").meta.endpoint_url)
    yield repo
    kit.stop()

def test_create_and_list_users(repo):
    repo.create_user("alice")
    users = repo.list_users()
    assert users[0]["UserName"] == "alice"

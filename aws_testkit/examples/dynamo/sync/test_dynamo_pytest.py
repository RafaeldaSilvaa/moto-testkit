# test_dynamodb_pytest.py
import pytest
from aws_testkit.src import MotoTestKit
from dynamodb_repository import DynamoDBRepository


@pytest.fixture
def repo():
    kit = MotoTestKit(auto_start=True)
    repo = DynamoDBRepository(endpoint_url=kit.get_client("dynamodb").meta.endpoint_url)
    repo.create_table(
        table_name="Users",
        key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
        provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    )
    yield repo
    kit.stop()


def test_put_and_get_item(repo):
    repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
    item = repo.get_item("Users", {"id": {"S": "1"}})
    assert item["name"]["S"] == "Alice"


def test_query_items(repo):
    repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
    items = repo.query_items(
        "Users",
        "id = :id",
        {":id": {"S": "1"}}
    )
    assert len(items) == 1
    assert items[0]["name"]["S"] == "Alice"

from typing import List, Dict, Any

from aws_testkit.examples.dynamo.synchronous.dynamodb_synchronous_repository import DynamoDBRepository
from aws_testkit.src.moto_testkit import use_moto_testkit, AutoMotoTestKit

@use_moto_testkit(auto_start=True, patch_aiobotocore=False)
def test_put_and_get_item_with_decorator(moto_testkit) -> None:
    """Insert and get an item using @use_moto_testkit decorator."""
    repo = DynamoDBRepository(endpoint_url=moto_testkit.get_client("dynamodb").meta.endpoint_url)
    repo.create_table(
        table_name="Users",
        key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
        provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    )
    repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
    item: Dict[str, Any] = repo.get_item("Users", {"id": {"S": "1"}})
    assert item["name"]["S"] == "Alice"


@use_moto_testkit(auto_start=True, patch_aiobotocore=False)
def test_query_items_with_decorator(moto_testkit) -> None:
    """Insert and query items using @use_moto_testkit decorator."""
    repo = DynamoDBRepository(endpoint_url=moto_testkit.get_client("dynamodb").meta.endpoint_url)
    repo.create_table(
        table_name="Users",
        key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
        provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    )
    repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
    items: List[Dict[str, Any]] = repo.query_items(
        "Users", "id = :id", {":id": {"S": "1"}}
    )
    assert len(items) == 1
    assert items[0]["name"]["S"] == "Alice"
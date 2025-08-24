import pytest
from typing import Generator, List, Dict, Any

from aws_testkit.examples.dynamo.synchronous.dynamodb_synchronous_repository import DynamoDBRepository
from aws_testkit.src import MotoTestKit


@pytest.fixture
def moto_testkit() -> Generator[MotoTestKit, None, None]:
    """Starts and stops the MotoTestKit for DynamoDB."""
    kit_instance = MotoTestKit(auto_start=True, patch_aiobotocore=False)
    yield kit_instance
    kit_instance.stop()


@pytest.fixture
def dynamodb_repo(moto_testkit: MotoTestKit) -> Generator[DynamoDBRepository, None, None]:
    """Provides a DynamoDBRepository configured with a test table."""
    repo_instance = DynamoDBRepository(
        endpoint_url=moto_testkit.get_client("dynamodb").meta.endpoint_url
    )
    repo_instance.create_table(
        table_name="Users",
        key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
        provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    )
    yield repo_instance


def test_put_and_get_item(dynamodb_repo: DynamoDBRepository) -> None:
    """Insert an item and retrieve it from the table."""
    dynamodb_repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
    item: Dict[str, Any] = dynamodb_repo.get_item("Users", {"id": {"S": "1"}})
    assert item["name"]["S"] == "Alice"


def test_query_items(dynamodb_repo: DynamoDBRepository) -> None:
    """Insert and query items by key."""
    dynamodb_repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
    items: List[Dict[str, Any]] = dynamodb_repo.query_items(
        "Users", "id = :id", {":id": {"S": "1"}}
    )
    assert len(items) == 1
    assert items[0]["name"]["S"] == "Alice"

import pytest
from aws_testkit.examples.dynamo.synchronous.dynamodb_synchronous_repository import DynamoDBRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit
import boto3

@pytest.fixture(scope="function")
def repo():
    """Fixture que cria um repositório com o ambiente Moto mockado."""
    with AutoMotoTestKit(auto_start=True) as mt:
        dynamodb_client = boto3.client("dynamodb")
        repo_instance = DynamoDBRepository(endpoint_url=dynamodb_client.meta.endpoint_url)

        repo_instance.create_table(
            table_name="Users",
            key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
            attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
            provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        yield repo_instance

def test_put_and_get_item(repo):
    """Teste usando a fixture 'repo' para acessar o repositório."""
    repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
    item = repo.get_item("Users", {"id": {"S": "1"}})
    assert item["name"]["S"] == "Alice"

def test_query_items(repo):
    """Outro teste usando a mesma fixture."""
    repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "User1"}})
    repo.put_item("Users", {"id": {"S": "2"}, "name": {"S": "User2"}})

    items = repo.query_items(
        "Users",
        "id = :id",
        {":id": {"S": "2"}}
    )
    assert len(items) == 1
    assert items[0]["name"]["S"] == "User2"
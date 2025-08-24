import pytest
import pytest_asyncio
from typing import AsyncGenerator

from aws_testkit.examples.dynamo.asynchronous.dynamo_asynchronous_repository import DynamoDBAsyncRepository
from aws_testkit.src import MotoTestKit


@pytest_asyncio.fixture
async def moto_kit() -> AsyncGenerator[MotoTestKit, None]:
    """Async fixture to start and stop MotoTestKit for DynamoDB."""
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    await kit.close_async_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_dynamodb_put_and_get(moto_kit: MotoTestKit) -> None:
    """Create table, insert item, and retrieve it from DynamoDB."""
    repo = DynamoDBAsyncRepository()
    await repo.create_table(
        "MinhaTabela",
        [{"AttributeName": "id", "KeyType": "HASH"}],
        [{"AttributeName": "id", "AttributeType": "S"}],
        {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    )
    await repo.put_item("MinhaTabela", {"id": {"S": "123"}})
    item = await repo.get_item("MinhaTabela", {"id": {"S": "123"}})
    assert item["id"]["S"] == "123"

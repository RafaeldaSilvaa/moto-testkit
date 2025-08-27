from typing import Any, Dict

import pytest

from examples.dynamo.asynchronous.dynamo_asynchronous_repository import \
    DynamoDBAsyncRepository
from src.moto_testkit import AutoMotoTestKit


@pytest.mark.asyncio
async def test_dynamodb_put_and_get_with_context_manager() -> None:
    """Using MotoTestKit as async context manager for DynamoDB tests."""
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
        repo = DynamoDBAsyncRepository()
        await repo.create_table(
            "MinhaTabela",
            [{"AttributeName": "id", "KeyType": "HASH"}],
            [{"AttributeName": "id", "AttributeType": "S"}],
            {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        await repo.put_item("MinhaTabela", {"id": {"S": "123"}})
        item: Dict[str, Any] = await repo.get_item("MinhaTabela", {"id": {"S": "123"}})
        assert item["id"]["S"] == "123"

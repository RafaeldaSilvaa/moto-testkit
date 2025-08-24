import unittest
from typing import Any, Dict
from aws_testkit.examples.dynamo.asynchronous.dynamo_asynchronous_repository import DynamoDBAsyncRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestDynamoDBAsyncRepositoryWithContextManager(unittest.IsolatedAsyncioTestCase):
    """Async unittest using MotoTestKit as async context manager."""

    async def test_put_and_get_item(self) -> None:
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
            repo = DynamoDBAsyncRepository()
            await repo.create_table(
                "MinhaTabela",
                [{"AttributeName": "id", "KeyType": "HASH"}],
                [{"AttributeName": "id", "AttributeType": "S"}],
                {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            )
            await repo.put_item("MinhaTabela", {"id": {"S": "123"}})
            item: Dict[str, Any] = await repo.get_item("MinhaTabela", {"id": {"S": "123"}})
            self.assertEqual(item["id"]["S"], "123")

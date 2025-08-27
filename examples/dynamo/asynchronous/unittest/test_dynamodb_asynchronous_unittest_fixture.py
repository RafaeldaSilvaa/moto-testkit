import unittest
from typing import Any, Dict

from examples.dynamo.asynchronous.dynamo_asynchronous_repository import DynamoDBAsyncRepository
from src import MotoTestKit


class TestDynamoDBAsyncRepositoryWithFixture(unittest.IsolatedAsyncioTestCase):
    """Async unittest with setUp/tearDown fixture pattern using MotoTestKit."""

    async def asyncSetUp(self) -> None:
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        self.repo = DynamoDBAsyncRepository()

    async def asyncTearDown(self) -> None:
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_put_and_get_item(self) -> None:
        await self.repo.create_table(
            "MinhaTabela",
            [{"AttributeName": "id", "KeyType": "HASH"}],
            [{"AttributeName": "id", "AttributeType": "S"}],
            {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        await self.repo.put_item("MinhaTabela", {"id": {"S": "123"}})
        item: Dict[str, Any] = await self.repo.get_item(
            "MinhaTabela", {"id": {"S": "123"}}
        )
        self.assertEqual(item["id"]["S"], "123")

import unittest
from typing import Any, Dict

from examples.dynamo.asynchronous.dynamo_asynchronous_repository import DynamoDBAsyncRepository
from src.moto_testkit import use_moto_testkit


@use_moto_testkit(patch_aiobotocore=True)
class TestDynamoDBAsyncRepositoryDecoratorOnClass(unittest.IsolatedAsyncioTestCase):
    """Async unittest with @use_moto_testkit applied at class level."""

    async def test_put_and_get_item(self, moto_testkit) -> None:
        repo = DynamoDBAsyncRepository()
        await repo.create_table(
            "MinhaTabela",
            [{"AttributeName": "id", "KeyType": "HASH"}],
            [{"AttributeName": "id", "AttributeType": "S"}],
            {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        await repo.put_item("MinhaTabela", {"id": {"S": "123"}})
        item: Dict[str, Any] = await repo.get_item("MinhaTabela", {"id": {"S": "123"}})
        self.assertEqual(item["id"]["S"], "123")


class TestDynamoDBAsyncRepositoryDecoratorOnMethods(unittest.IsolatedAsyncioTestCase):
    """Async unittest with @use_moto_testkit applied on each method."""

    @use_moto_testkit(patch_aiobotocore=True)
    async def test_put_and_get_item(self, moto_testkit) -> None:
        repo = DynamoDBAsyncRepository()
        await repo.create_table(
            "MinhaTabela",
            [{"AttributeName": "id", "KeyType": "HASH"}],
            [{"AttributeName": "id", "AttributeType": "S"}],
            {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        await repo.put_item("MinhaTabela", {"id": {"S": "123"}})
        item: Dict[str, Any] = await repo.get_item("MinhaTabela", {"id": {"S": "123"}})
        self.assertEqual(item["id"]["S"], "123")

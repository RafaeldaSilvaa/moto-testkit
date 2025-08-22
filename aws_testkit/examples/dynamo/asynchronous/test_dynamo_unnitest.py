import unittest

from aws_testkit.examples.dynamo.asynchronous.dynamo import DynamoDBAsyncRepository
from aws_testkit.src import MotoTestKit


class TestDynamoDBRepositoryWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        self.repo = DynamoDBAsyncRepository()

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_put_and_get_item(self):
        await self.repo.create_table(
            "MinhaTabela",
            [{"AttributeName": "id", "KeyType": "HASH"}],
            [{"AttributeName": "id", "AttributeType": "S"}],
            {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )
        await self.repo.put_item("MinhaTabela", {"id": {"S": "123"}})
        item = await self.repo.get_item("MinhaTabela", {"id": {"S": "123"}})
        self.assertEqual(item["id"]["S"], "123")

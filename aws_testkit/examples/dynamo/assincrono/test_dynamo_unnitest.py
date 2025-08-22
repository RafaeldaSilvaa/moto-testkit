import unittest

from aws_testkit.src import MotoTestKit


class TestDynamoDBWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_dynamodb_put_and_get_item(self):
        dynamo_client = await self.kit.get_async_client("dynamodb")

        table_name = "MinhaTabela"
        await dynamo_client.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )

        await dynamo_client.put_item(
            TableName=table_name,
            Item={"id": {"S": "123"}}
        )

        resp = await dynamo_client.get_item(
            TableName=table_name,
            Key={"id": {"S": "123"}}
        )

        self.assertEqual(resp["Item"]["id"]["S"], "123")

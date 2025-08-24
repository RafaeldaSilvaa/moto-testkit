import unittest

from aws_testkit.examples.dynamo.synchronous.dynamodb_synchronous_repository import DynamoDBRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestDynamoDBRepositoryContextManager(unittest.TestCase):

    def test_put_and_get_item(self):
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=False) as kit:
            repo = DynamoDBRepository(endpoint_url=kit.get_client("dynamodb").meta.endpoint_url)
            repo.create_table(
                table_name="Users",
                key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
                attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
                provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            )
            repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
            item = repo.get_item("Users", {"id": {"S": "1"}})
            self.assertEqual(item["name"]["S"], "Alice")

    def test_query_items(self):
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=False) as kit:
            repo = DynamoDBRepository(endpoint_url=kit.get_client("dynamodb").meta.endpoint_url)
            repo.create_table(
                table_name="Users",
                key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
                attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
                provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            )
            repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
            items = repo.query_items("Users", "id = :id", {":id": {"S": "1"}})
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["name"]["S"], "Alice")

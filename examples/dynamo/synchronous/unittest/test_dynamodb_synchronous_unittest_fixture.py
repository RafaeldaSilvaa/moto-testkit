import unittest

from examples.dynamo.synchronous.dynamodb_synchronous_repository import DynamoDBRepository
from src import MotoTestKit


class TestDynamoDBRepositoryFixture(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=False)
        self.repo = DynamoDBRepository(
            endpoint_url=self.kit.get_client("dynamodb").meta.endpoint_url
        )
        self.repo.create_table(
            table_name="Users",
            key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
            attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
            provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

    def tearDown(self):
        self.kit.stop()

    def test_put_and_get_item(self):
        self.repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
        item = self.repo.get_item("Users", {"id": {"S": "1"}})
        self.assertEqual(item["name"]["S"], "Alice")

    def test_query_items(self):
        self.repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
        items = self.repo.query_items("Users", "id = :id", {":id": {"S": "1"}})
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"]["S"], "Alice")

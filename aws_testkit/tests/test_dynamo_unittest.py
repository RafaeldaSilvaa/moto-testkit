# tests/test_dynamo_unittest.py
import unittest

from aws_testkit.src import MotoTestKit, DynamoItemModel


class DynamoTestCase(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True)  # auto_start inicia por você
        # opcional: self.kit.start()
        self.helper = self.kit.dynamo_helper()
        self.helper.create_table("users")

    def tearDown(self):
        # no teardown assincrono aqui; stop apenas
        self.kit.stop()

    def test_put_get(self):
        model = DynamoItemModel(table="users", item={"id": {"S": "1"}, "name": {"S": "Rafael"}})
        self.helper.put_item(model)
        got = self.helper.get_item("users", {"id": {"S": "1"}})
        self.assertIn("Item", got)
        self.assertEqual(got["Item"]["name"]["S"], "Rafael")

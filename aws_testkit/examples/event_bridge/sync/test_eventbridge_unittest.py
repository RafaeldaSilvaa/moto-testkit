import unittest
from aws_testkit.src import MotoTestKit
from eventbridge_repository import EventBridgeRepository

class TestEventBridgeRepository(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True)
        self.repo = EventBridgeRepository(endpoint_url=self.kit.get_client("events").meta.endpoint_url)

    def tearDown(self):
        self.kit.stop()

    def test_put_and_list_rules(self):
        self.repo.put_rule("my-rule", '{"source": ["app.test"]}')
        rules = self.repo.list_rules()
        self.assertIn("my-rule", rules)

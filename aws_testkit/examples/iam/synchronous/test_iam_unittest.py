import unittest
from aws_testkit.src import MotoTestKit
from iam_repository import IAMRepository

class TestIAMRepository(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True)
        self.repo = IAMRepository(endpoint_url=self.kit.get_client("iam").meta.endpoint_url)

    def tearDown(self):
        self.kit.stop()

    def test_create_and_list_users(self):
        self.repo.create_user("alice")
        users = self.repo.list_users()
        self.assertEqual(users[0]["UserName"], "alice")

import unittest

from examples.iam.synchronous.iam_synchronous_repository import IAMRepository
from src import MotoTestKit


class TestIAMRepositoryFixtureMotoTestKit(unittest.TestCase):
    def setUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(auto_start=True)
        self.repository: IAMRepository = IAMRepository(
            endpoint_url=self.moto_testkit.get_client("iam").meta.endpoint_url
        )

    def tearDown(self) -> None:
        self.moto_testkit.stop()

    def test_create_and_list_users(self) -> None:
        user_name: str = "alice"
        self.repository.create_user(user_name)
        users = self.repository.list_users()

        self.assertEqual(users[0]["UserName"], user_name)

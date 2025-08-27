import unittest

from aws_testkit.examples.iam.synchronous.iam_synchronous_repository import IAMRepository
from aws_testkit.src.moto_testkit import use_moto_testkit, AutoMotoTestKit


class TestIAMRepositoryWithDecorator(unittest.TestCase):
    @use_moto_testkit(auto_start=True)
    def test_create_and_list_users(self, moto_testkit: AutoMotoTestKit) -> None:
        repository: IAMRepository = IAMRepository(endpoint_url=moto_testkit.get_client("iam").meta.endpoint_url)
        user_name: str = "alice"

        repository.create_user(user_name)
        users = repository.list_users()

        self.assertEqual(users[0]["UserName"], user_name)

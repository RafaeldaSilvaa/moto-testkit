import unittest

from examples.iam.asynchronous.iam_asynchronous_repository import IAMAsyncRepository
from src.moto_testkit import AutoMotoTestKit, use_moto_testkit


class TestIAMRepositoryWithDecorator(unittest.IsolatedAsyncioTestCase):
    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_create_and_list_users(self, moto_testkit: AutoMotoTestKit) -> None:
        repository: IAMAsyncRepository = IAMAsyncRepository()
        user_name: str = "usuario_teste"

        await repository.create_user(user_name)
        users = await repository.list_users()
        retrieved_names = [user["UserName"] for user in users]

        self.assertIn(user_name, retrieved_names)

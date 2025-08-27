import unittest

from examples.iam.asynchronous.iam_asynchronous_repository import \
    IAMAsyncRepository
from src import MotoTestKit


class TestIAMRepositoryFixtureMotoTestKit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(
            auto_start=True, patch_aiobotocore=True
        )
        self.repository: IAMAsyncRepository = IAMAsyncRepository()

    async def asyncTearDown(self) -> None:
        await self.moto_testkit.close_async_clients()
        self.moto_testkit.stop()

    async def test_create_and_list_users(self) -> None:
        user_name: str = "usuario_teste"
        await self.repository.create_user(user_name)
        users = await self.repository.list_users()
        retrieved_names = [user["UserName"] for user in users]

        self.assertIn(user_name, retrieved_names)

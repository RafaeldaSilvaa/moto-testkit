import unittest

from aws_testkit.examples.iam.asynchronous.iam_async_repository import IAMAsyncRepository
from aws_testkit.src import MotoTestKit


class TestIAMRepositoryWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        self.repo = IAMAsyncRepository()

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_create_and_list_users(self):
        await self.repo.create_user("usuario_teste")
        users = await self.repo.list_users()
        nomes = [u["UserName"] for u in users]
        self.assertIn("usuario_teste", nomes)

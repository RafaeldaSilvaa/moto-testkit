import unittest

from aws_testkit.src import MotoTestKit


class TestIAMWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_iam_create_and_list_roles(self):
        iam_client = await self.kit.get_async_client("iam")

        role_name = "MinhaRole"
        assume_role_policy = '{"Version": "2012-10-17","Statement": [{"Effect": "Allow","Principal": {"Service": "lambda.amazonaws.com"},"Action": "sts:AssumeRole"}]}'

        await iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_role_policy
        )

        resp = await iam_client.list_roles()
        roles = [r["RoleName"] for r in resp.get("Roles", [])]

        self.assertIn(role_name, roles, f"A role '{role_name}' não foi encontrada.")

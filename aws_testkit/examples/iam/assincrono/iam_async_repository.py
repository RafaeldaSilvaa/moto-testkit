import aioboto3
from typing import Optional


class IAMAsyncRepository:
    def __init__(self, endpoint_url: Optional[str] = None):
        self.endpoint_url = endpoint_url

    async def create_user(self, user_name: str):
        async with aioboto3.Session().client("iam", endpoint_url=self.endpoint_url) as client:
            return await client.create_user(UserName=user_name)

    async def list_users(self):
        async with aioboto3.Session().client("iam", endpoint_url=self.endpoint_url) as client:
            resp = await client.list_users()
            return resp["Users"]

    async def create_role(self, role_name: str, assume_role_policy_document: str):
        async with aioboto3.Session().client("iam", endpoint_url=self.endpoint_url) as client:
            return await client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=assume_role_policy_document
            )

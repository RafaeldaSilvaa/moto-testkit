import boto3
from typing import Optional


class IAMRepository:
    def __init__(self, endpoint_url: Optional[str] = None):
        self.client = boto3.client("iam", endpoint_url=endpoint_url)

    def create_user(self, user_name: str):
        return self.client.create_user(UserName=user_name)

    def list_users(self):
        return self.client.list_users()["Users"]

    def create_role(self, role_name: str, assume_role_policy_document: str):
        return self.client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_role_policy_document
        )

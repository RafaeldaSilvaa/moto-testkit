import pytest

from examples.iam.asynchronous.iam_asynchronous_repository import IAMAsyncRepository
from src.moto_testkit import AutoMotoTestKit


@pytest.mark.asyncio
async def test_create_and_list_users_with_context_manager() -> None:
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
        repository: IAMAsyncRepository = IAMAsyncRepository()
        user_name: str = "usuario_teste"

        await repository.create_user(user_name)
        users = await repository.list_users()
        retrieved_names = [user["UserName"] for user in users]

        assert user_name in retrieved_names

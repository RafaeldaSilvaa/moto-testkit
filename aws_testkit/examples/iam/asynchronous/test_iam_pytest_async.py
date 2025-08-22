import pytest
import pytest
import pytest_asyncio

from aws_testkit.examples.iam.asynchronous.iam_async_repository import IAMAsyncRepository
from aws_testkit.src import MotoTestKit

@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    kit.close_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_iam_create_and_list_users(moto_kit):
    repo = IAMAsyncRepository()
    await repo.create_user("usuario_teste")
    users = await repo.list_users()
    nomes = [u["UserName"] for u in users]
    assert "usuario_teste" in nomes

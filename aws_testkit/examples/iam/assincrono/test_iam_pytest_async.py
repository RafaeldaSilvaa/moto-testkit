import pytest
import pytest
import pytest_asyncio

from aws_testkit.src import MotoTestKit

@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    kit.close_clients()
    kit.stop()
    
@pytest.mark.asyncio
async def test_iam_create_and_list_users(moto_kit):
    iam_client = await moto_kit.get_async_client("iam")

    await iam_client.create_user(UserName="usuario_teste")

    resp = await iam_client.list_users()
    nomes = [u["UserName"] for u in resp.get("Users", [])]

    assert "usuario_teste" in nomes

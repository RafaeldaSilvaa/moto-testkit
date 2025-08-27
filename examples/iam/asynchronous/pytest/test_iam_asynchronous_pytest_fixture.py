import pytest
import pytest_asyncio

from examples.iam.asynchronous.iam_asynchronous_repository import \
    IAMAsyncRepository
from src import MotoTestKit


@pytest_asyncio.fixture
async def moto_testkit_fixture() -> MotoTestKit:
    """Inicializa o MotoTestKit antes do teste e garante encerramento adequado."""
    testkit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield testkit
    await testkit.close_async_clients()
    testkit.stop()


@pytest.mark.asyncio
async def test_create_and_list_users_with_fixture(
    moto_testkit_fixture: MotoTestKit,
) -> None:
    repository: IAMAsyncRepository = IAMAsyncRepository()
    user_name: str = "usuario_teste"

    await repository.create_user(user_name)
    users = await repository.list_users()
    retrieved_names = [user["UserName"] for user in users]

    assert user_name in retrieved_names

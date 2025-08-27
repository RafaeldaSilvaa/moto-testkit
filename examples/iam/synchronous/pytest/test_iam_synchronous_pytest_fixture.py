import pytest

from examples.iam.synchronous.iam_synchronous_repository import \
    IAMRepository
from src import MotoTestKit


@pytest.fixture
def moto_testkit_fixture() -> IAMRepository:
    """Inicializa o MotoTestKit e retorna o repositório configurado."""
    moto_testkit = MotoTestKit(auto_start=True)
    repository = IAMRepository(
        endpoint_url=moto_testkit.get_client("iam").meta.endpoint_url
    )
    yield repository
    moto_testkit.stop()


def test_create_and_list_users_with_fixture(
    moto_testkit_fixture: IAMRepository,
) -> None:
    user_name: str = "alice"
    moto_testkit_fixture.create_user(user_name)
    users = moto_testkit_fixture.list_users()

    assert users[0]["UserName"] == user_name

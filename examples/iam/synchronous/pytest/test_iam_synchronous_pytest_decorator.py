from examples.iam.synchronous.iam_synchronous_repository import \
    IAMRepository
from src.moto_testkit import AutoMotoTestKit, use_moto_testkit


@use_moto_testkit(auto_start=True)
def test_create_and_list_users_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository = IAMRepository(
        endpoint_url=moto_testkit.get_client("iam").meta.endpoint_url
    )
    user_name: str = "alice"

    repository.create_user(user_name)
    users = repository.list_users()

    assert users[0]["UserName"] == user_name

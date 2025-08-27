from examples.iam.synchronous.iam_synchronous_repository import IAMRepository
from src.moto_testkit import AutoMotoTestKit


def test_create_and_list_users_with_context_manager() -> None:
    with AutoMotoTestKit(auto_start=True) as moto_testkit:
        repository = IAMRepository(
            endpoint_url=moto_testkit.get_client("iam").meta.endpoint_url
        )
        user_name: str = "alice"

        repository.create_user(user_name)
        users = repository.list_users()

        assert users[0]["UserName"] == user_name

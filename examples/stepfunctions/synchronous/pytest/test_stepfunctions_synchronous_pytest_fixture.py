import pytest

from examples.stepfunctions.synchronous.stepfunctions_synchronous_repository import \
    StepFunctionsRepository
from src import MotoTestKit


@pytest.fixture
def moto_testkit_fixture() -> StepFunctionsRepository:
    moto_testkit = MotoTestKit(auto_start=True)
    repository = StepFunctionsRepository(
        endpoint_url=moto_testkit.get_client("stepfunctions").meta.endpoint_url
    )
    yield repository
    moto_testkit.stop()


def test_create_state_machine_with_fixture(
    moto_testkit_fixture: StepFunctionsRepository,
) -> None:
    definition = (
        '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
    )
    role_arn = "arn:aws:iam::123456789012:role/DummyRole"
    sm = moto_testkit_fixture.create_state_machine(
        "MyStateMachine", definition, role_arn
    )
    assert "stateMachineArn" in sm

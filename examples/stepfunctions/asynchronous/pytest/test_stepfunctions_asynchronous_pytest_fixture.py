import pytest
import pytest_asyncio

from examples.stepfunctions.asynchronous.stepfunctions_asynchronous_repository import \
    StepFunctionsAsyncRepository
from src import MotoTestKit


@pytest_asyncio.fixture
async def moto_testkit_fixture() -> MotoTestKit:
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    await kit.close_async_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_stepfunctions_create_and_start_execution_with_fixture(
    moto_testkit_fixture: MotoTestKit,
) -> None:
    repository = StepFunctionsAsyncRepository()
    definition = (
        '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
    )
    sm = await repository.create_state_machine(
        name="MinhaStateMachine",
        definition=definition,
        role_arn="arn:aws:iam::123456789012:role/DummyRole",
    )
    exec_resp = await repository.start_execution(sm["stateMachineArn"], "{}")
    assert "executionArn" in exec_resp

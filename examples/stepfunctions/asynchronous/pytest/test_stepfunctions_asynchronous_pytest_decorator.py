import pytest

from examples.stepfunctions.asynchronous.stepfunctions_asynchronous_repository import StepFunctionsAsyncRepository
from src.moto_testkit import AutoMotoTestKit, use_moto_testkit


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_stepfunctions_create_and_start_execution_with_decorator(
    moto_testkit: AutoMotoTestKit,
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

import pytest
import pytest_asyncio

from aws_testkit.examples.stepfunctions.assincrono.stepfunctions_async_repository import StepFunctionsAsyncRepository
from aws_testkit.src import MotoTestKit
import json

@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    kit.close_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_stepfunctions_create_and_start_execution(moto_kit):
    repo = StepFunctionsAsyncRepository()
    definition = '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
    sm = await repo.create_state_machine(
        "MinhaStateMachine",
        definition,
        "arn:aws:iam::123456789012:role/DummyRole"
    )
    exec_resp = await repo.start_execution(sm["stateMachineArn"], "{}")
    assert "executionArn" in exec_resp

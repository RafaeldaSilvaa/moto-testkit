import unittest
from aws_testkit.examples.stepfunctions.asynchronous.stepfunctions_asynchronous_repository import (
    StepFunctionsAsyncRepository,
)
from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestStepFunctionsRepositoryWithContextManager(unittest.IsolatedAsyncioTestCase):
    async def test_create_and_start_execution(self) -> None:
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
            repository = StepFunctionsAsyncRepository()
            definition = '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
            sm = await repository.create_state_machine(
                "MinhaStateMachine", definition, "arn:aws:iam::123456789012:role/DummyRole"
            )
            exec_resp = await repository.start_execution(sm["stateMachineArn"], "{}")
            self.assertIn("executionArn", exec_resp)

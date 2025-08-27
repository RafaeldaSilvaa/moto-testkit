import unittest

from aws_testkit.examples.stepfunctions.asynchronous.stepfunctions_asynchronous_repository import \
    StepFunctionsAsyncRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit, use_moto_testkit


class TestStepFunctionsRepositoryWithDecorator(unittest.IsolatedAsyncioTestCase):
    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_create_and_start_execution(
        self, moto_testkit: AutoMotoTestKit
    ) -> None:
        repository = StepFunctionsAsyncRepository()
        definition = (
            '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
        )
        sm = await repository.create_state_machine(
            "MinhaStateMachine", definition, "arn:aws:iam::123456789012:role/DummyRole"
        )
        exec_resp = await repository.start_execution(sm["stateMachineArn"], "{}")
        self.assertIn("executionArn", exec_resp)

import unittest

from examples.stepfunctions.asynchronous.stepfunctions_asynchronous_repository import \
    StepFunctionsAsyncRepository
from src import MotoTestKit


class TestStepFunctionsRepositoryFixtureMotoTestKit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(
            auto_start=True, patch_aiobotocore=True
        )
        self.repository: StepFunctionsAsyncRepository = StepFunctionsAsyncRepository()

    async def asyncTearDown(self) -> None:
        await self.moto_testkit.close_async_clients()
        self.moto_testkit.stop()

    async def test_create_and_start_execution(self) -> None:
        definition = (
            '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
        )
        sm = await self.repository.create_state_machine(
            "MinhaStateMachine", definition, "arn:aws:iam::123456789012:role/DummyRole"
        )
        exec_resp = await self.repository.start_execution(sm["stateMachineArn"], "{}")
        self.assertIn("executionArn", exec_resp)

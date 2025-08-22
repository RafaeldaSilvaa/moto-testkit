import unittest

from aws_testkit.examples.stepfunctions.asynchronous.stepfunctions_async_repository import StepFunctionsAsyncRepository
from aws_testkit.src import MotoTestKit


class TestStepFunctionsRepositoryWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        self.repo = StepFunctionsAsyncRepository()

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_create_and_start_execution(self):
        definition = '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
        sm = await self.repo.create_state_machine("MinhaStateMachine", definition, "arn:aws:iam::123456789012:role/DummyRole")
        exec_resp = await self.repo.start_execution(sm["stateMachineArn"], "{}")
        self.assertIn("executionArn", exec_resp)

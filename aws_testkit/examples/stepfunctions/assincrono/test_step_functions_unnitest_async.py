import unittest

from aws_testkit.src import MotoTestKit


class TestStepFunctionsWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_stepfunctions_create_and_start_execution(self):
        sf_client = await self.kit.get_async_client("stepfunctions")

        sm_name = "MinhaStateMachine"
        definition = '{"Comment": "Exemplo", "StartAt": "Passo1", "States": {"Passo1": {"Type": "Succeed"}}}'

        create_resp = await sf_client.create_state_machine(
            name=sm_name,
            definition=definition,
            roleArn="arn:aws:iam::123456789012:role/DummyRole"
        )
        sm_arn = create_resp["stateMachineArn"]

        exec_resp = await sf_client.start_execution(
            stateMachineArn=sm_arn,
            input="{}"
        )

        self.assertIn(sm_name, sm_arn)
        self.assertIn("executionArn", exec_resp)

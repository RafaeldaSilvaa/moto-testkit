import unittest

from examples.stepfunctions.synchronous.stepfunctions_synchronous_repository import StepFunctionsRepository
from src import MotoTestKit


class TestStepFunctionsRepositoryFixtureMotoTestKit(unittest.TestCase):
    def setUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(auto_start=True)
        self.repository: StepFunctionsRepository = StepFunctionsRepository(
            endpoint_url=self.moto_testkit.get_client("stepfunctions").meta.endpoint_url
        )

    def tearDown(self) -> None:
        self.moto_testkit.stop()

    def test_create_state_machine(self) -> None:
        definition = (
            '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
        )
        role_arn = "arn:aws:iam::123456789012:role/DummyRole"
        sm = self.repository.create_state_machine(
            "MyStateMachine", definition, role_arn
        )
        self.assertIn("stateMachineArn", sm)

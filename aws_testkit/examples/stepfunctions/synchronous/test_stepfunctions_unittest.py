import unittest
from aws_testkit.src import MotoTestKit
from stepfunctions_repository import StepFunctionsRepository

class TestStepFunctionsRepository(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True)
        self.repo = StepFunctionsRepository(endpoint_url=self.kit.get_client("stepfunctions").meta.endpoint_url)

    def tearDown(self):
        self.kit.stop()

    def test_create_state_machine(self):
        definition = '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
        role_arn = "arn:aws:iam::123456789012:role/DummyRole"
        sm = self.repo.create_state_machine("MyStateMachine", definition, role_arn)
        self.assertIn("stateMachineArn", sm)

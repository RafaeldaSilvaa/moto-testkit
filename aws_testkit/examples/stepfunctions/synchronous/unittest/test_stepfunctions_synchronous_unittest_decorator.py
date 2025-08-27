import unittest

from aws_testkit.examples.stepfunctions.synchronous.stepfunctions_synchronous_repository import StepFunctionsRepository
from aws_testkit.src.moto_testkit import use_moto_testkit, AutoMotoTestKit


class TestStepFunctionsRepositoryWithDecorator(unittest.TestCase):
    @use_moto_testkit(auto_start=True)
    def test_create_state_machine(self, moto_testkit: AutoMotoTestKit) -> None:
        repository = StepFunctionsRepository(endpoint_url=moto_testkit.get_client("stepfunctions").meta.endpoint_url)
        definition = '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
        role_arn = "arn:aws:iam::123456789012:role/DummyRole"
        sm = repository.create_state_machine("MyStateMachine", definition, role_arn)
        self.assertIn("stateMachineArn", sm)

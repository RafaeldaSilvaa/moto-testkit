import pytest
from aws_testkit.src import MotoTestKit
from stepfunctions_repository import StepFunctionsRepository

@pytest.fixture
def repo():
    kit = MotoTestKit(auto_start=True)
    repo = StepFunctionsRepository(endpoint_url=kit.get_client("stepfunctions").meta.endpoint_url)
    yield repo
    kit.stop()

def test_create_state_machine(repo):
    definition = '{"StartAt": "Hello", "States": {"Hello": {"Type": "Pass", "End": true}}}'
    role_arn = "arn:aws:iam::123456789012:role/DummyRole"
    sm = repo.create_state_machine("MyStateMachine", definition, role_arn)
    assert "stateMachineArn" in sm

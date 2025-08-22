import pytest
import pytest_asyncio

from aws_testkit.src import MotoTestKit
import json

@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    kit.close_clients()
    kit.stop()

@pytest.mark.asyncio
async def test_stepfunctions_create_and_list(moto_kit):
    sf_client = await moto_kit.get_async_client("stepfunctions")

    definition = json.dumps({
        "Comment": "Exemplo",
        "StartAt": "Passo1",
        "States": {
            "Passo1": {"Type": "Succeed"}
        }
    })

    arn = (await sf_client.create_state_machine(
        name="MinhaStateMachine",
        definition=definition,
        roleArn="arn:aws:iam::123456789012:role/DummyRole"
    ))["stateMachineArn"]

    resp = await sf_client.list_state_machines()
    arns = [sm["stateMachineArn"] for sm in resp.get("stateMachines", [])]

    assert arn in arns

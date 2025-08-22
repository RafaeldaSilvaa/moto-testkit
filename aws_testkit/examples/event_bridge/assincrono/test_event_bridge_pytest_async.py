import pytest

from aws_testkit.src import MotoTestKit
import pytest_asyncio

@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    await kit.close_async_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_eventbridge_put_rule_and_list(moto_kit):
    eb_client = await moto_kit.get_async_client("events")

    rule_name = "minha-regra-teste"
    await eb_client.put_rule(
        Name=rule_name,
        ScheduleExpression="rate(5 minutes)"
    )

    resp = await eb_client.list_rules()
    rules = [r["Name"] for r in resp.get("Rules", [])]

    assert rule_name in rules

import pytest
from aws_testkit.examples.event_bridge.asynchronous.eventbridge_async_repository import EventBridgeAsyncRepository
from aws_testkit.src.moto_testkit import use_moto_testkit, AutoMotoTestKit


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_put_rule_and_list_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository: EventBridgeAsyncRepository = EventBridgeAsyncRepository()
    rule_name: str = "regra-teste"

    await repository.put_rule(rule_name, '{"source": ["app.test"]}')
    rules = await repository.list_rules()

    assert rule_name in rules

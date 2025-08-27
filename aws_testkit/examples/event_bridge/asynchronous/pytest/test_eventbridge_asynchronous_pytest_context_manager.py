import pytest
from aws_testkit.examples.event_bridge.asynchronous.eventbridge_asynchronous_repository import (
    EventBridgeAsyncRepository,
)
from aws_testkit.src.moto_testkit import AutoMotoTestKit


@pytest.mark.asyncio
async def test_put_rule_and_list_with_context_manager() -> None:
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
        repository: EventBridgeAsyncRepository = EventBridgeAsyncRepository()
        rule_name: str = "regra-teste"

        await repository.put_rule(rule_name, '{"source": ["app.test"]}')
        rules = await repository.list_rules()

        assert rule_name in rules

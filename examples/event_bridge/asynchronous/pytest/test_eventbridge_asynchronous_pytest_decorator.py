import pytest

from examples.event_bridge.asynchronous.eventbridge_asynchronous_repository import \
    EventBridgeAsyncRepository
from src.moto_testkit import AutoMotoTestKit, use_moto_testkit


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_put_rule_and_list_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository: EventBridgeAsyncRepository = EventBridgeAsyncRepository()
    rule_name: str = "regra-teste"

    await repository.put_rule(rule_name, '{"source": ["app.test"]}')
    rules = await repository.list_rules()

    assert rule_name in rules

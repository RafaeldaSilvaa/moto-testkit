import pytest

from aws_testkit.examples.event_bridge.asynchronous.eventbridge_async_repository import EventBridgeAsyncRepository
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
    repo = EventBridgeAsyncRepository()
    await repo.put_rule("regra-teste", '{"source": ["app.test"]}')
    regras = await repo.list_rules()
    assert "regra-teste" in regras

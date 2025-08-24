import pytest
import pytest_asyncio
from aws_testkit.examples.event_bridge.asynchronous.eventbridge_async_repository import EventBridgeAsyncRepository
from aws_testkit.src import MotoTestKit


@pytest_asyncio.fixture
async def moto_testkit_fixture() -> MotoTestKit:
    """Inicializa o MotoTestKit para o teste e garante encerramento correto."""
    testkit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield testkit
    await testkit.close_async_clients()
    testkit.stop()


@pytest.mark.asyncio
async def test_put_rule_and_list_with_fixture(moto_testkit_fixture: MotoTestKit) -> None:
    repository: EventBridgeAsyncRepository = EventBridgeAsyncRepository()
    rule_name: str = "regra-teste"

    await repository.put_rule(rule_name, '{"source": ["app.test"]}')
    rules = await repository.list_rules()

    assert rule_name in rules

import asyncio
import pytest

from aws_testkit.src import MotoTestKit


@pytest.fixture(scope="session", autouse=True)
def moto_session():
    kit = MotoTestKit(verbose=False)
    kit.start()
    yield kit
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None
    if loop is None or not loop.is_running():
        asyncio.run(kit.close_clients())
    kit.stop()

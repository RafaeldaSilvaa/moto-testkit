import pytest
import pytest_asyncio

from aws_testkit.examples.cloudwatchlogs.assincrono.cloudwatchlogs_async_repository import CloudWatchLogsAsyncRepository
from aws_testkit.src import MotoTestKit

@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    kit.close_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_create_log_group_and_describe(moto_kit):
    # Arrange
    endpoint_url = moto_kit.get_client("logs").meta.endpoint_url
    repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    # Act
    await repo.create_log_group("meu-grupo-logs")
    grupos = await repo.describe_log_groups()

    # Assert
    nomes = [g["logGroupName"] for g in grupos]
    assert "meu-grupo-logs" in nomes


@pytest.mark.asyncio
async def test_create_log_stream(moto_kit):
    endpoint_url = moto_kit.get_client("logs").meta.endpoint_url
    repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    # Primeiro cria o grupo
    await repo.create_log_group("grupo-stream")
    # Depois cria o stream
    await repo.create_log_stream("grupo-stream", "stream-teste")

    # Valida usando cliente direto
    logs_client = await moto_kit.get_async_client("logs")
    resp = await logs_client.describe_log_streams(logGroupName="grupo-stream")
    nomes = [s["logStreamName"] for s in resp.get("logStreams", [])]

    assert "stream-teste" in nomes


@pytest.mark.asyncio
async def test_put_log_events(moto_kit):
    endpoint_url = moto_kit.get_client("logs").meta.endpoint_url
    repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    # Arrange
    await repo.create_log_group("grupo-logs")
    await repo.create_log_stream("grupo-logs", "stream-logs")

    # Act
    resp = await repo.put_log_events(
        "grupo-logs",
        "stream-logs",
        ["mensagem 1", "mensagem 2"]
    )

    # Assert
    assert "nextSequenceToken" in resp


@pytest.mark.asyncio
async def test_full_flow(moto_kit):
    """
    Testa o fluxo completo:
    - Cria grupo
    - Cria stream
    - Publica eventos
    - Lista grupos
    """
    endpoint_url = moto_kit.get_client("logs").meta.endpoint_url
    repo = CloudWatchLogsAsyncRepository(endpoint_url=endpoint_url)

    grupo = "grupo-completo"
    stream = "stream-completo"

    await repo.create_log_group(grupo)
    await repo.create_log_stream(grupo, stream)
    await repo.put_log_events(grupo, stream, ["log 1", "log 2"])

    grupos = await repo.describe_log_groups()
    nomes = [g["logGroupName"] for g in grupos]

    assert grupo in nomes

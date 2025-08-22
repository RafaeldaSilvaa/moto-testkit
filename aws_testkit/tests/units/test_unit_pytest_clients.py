import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from aws_testkit.src import ClientFactory


@pytest.fixture
def factory():
    return ClientFactory(region="us-east-1")


def test_get_client_retorna_mesma_instancia(factory):
    with patch("aws_testkit.src.clients.boto3.client") as mock_boto:
        mock_instance = MagicMock()
        mock_boto.return_value = mock_instance

        c1 = factory.get_client("s3")
        c2 = factory.get_client("s3")

        mock_boto.assert_called_once_with("s3", region_name="us-east-1")
        assert c1 is c2


def test_get_client_multiplos_servicos(factory):
    with patch("aws_testkit.src.clients.boto3.client") as mock_boto:
        instancias = {"s3": MagicMock(), "ec2": MagicMock()}
        mock_boto.side_effect = lambda nome, **_: instancias[nome]

        s3 = factory.get_client("s3")
        ec2 = factory.get_client("ec2")

        assert s3 is instancias["s3"]
        assert ec2 is instancias["ec2"]
        assert mock_boto.call_count == 2


def test_close_clients_com_metodo_close(factory):
    mock_client = MagicMock()
    factory._sync_clients["s3"] = mock_client

    factory.close_clients()

    mock_client.close.assert_called_once()
    assert "s3" not in factory._sync_clients


def test_close_clients_sem_metodo_close(factory):
    factory._sync_clients["s3"] = object()  # sem close()
    factory.close_clients()
    assert "s3" not in factory._sync_clients


def test_close_clients_cache_vazio(factory):
    factory.close_clients()  # não deve falhar


@pytest.mark.asyncio
async def test_close_async_clients_cache_vazio(factory):
    await factory.close_async_clients()  # não deve falhar


@pytest.mark.asyncio
async def test_close_async_clients_com_aexit(factory):
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aexit__ = AsyncMock()
    factory._async_clients["s3"] = (MagicMock(), mock_cm, mock_client)

    await factory.close_async_clients()

    mock_cm.__aexit__.assert_awaited_once_with(None, None, None)
    assert "s3" not in factory._async_clients


@pytest.mark.asyncio
async def test_close_async_clients_com_excecao_no_aexit(factory):
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aexit__ = AsyncMock(side_effect=RuntimeError("falha"))
    factory._async_clients["s3"] = (MagicMock(), mock_cm, mock_client)

    await factory.close_async_clients()

    assert "s3" not in factory._async_clients


@pytest.mark.asyncio
async def test_get_async_client_retorna_mesma_instancia(factory):
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_client

    with patch("aws_testkit.src.clients.aioboto3.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session.client.return_value = mock_cm
        mock_session_cls.return_value = mock_session

        c1 = await factory.get_async_client("s3")
        c2 = await factory.get_async_client("s3")

        mock_session.client.assert_called_once_with("s3", region_name="us-east-1")
        assert c1 is c2


@pytest.mark.asyncio
async def test_get_async_client_com_erro_no_aenter(factory):
    mock_cm = AsyncMock()
    mock_cm.__aenter__.side_effect = RuntimeError("falha")
    mock_cm.__aexit__ = AsyncMock()

    with patch("aws_testkit.src.clients.aioboto3.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session.client.return_value = mock_cm
        mock_session_cls.return_value = mock_session

        with pytest.raises(RuntimeError):
            await factory.get_async_client("s3")

        mock_cm.__aexit__.assert_awaited_once_with(None, None, None)

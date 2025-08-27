from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aws_testkit.src import ClientFactory


@pytest.fixture
def factory():
    return ClientFactory(region="us-east-1")


def test_get_client_returns_same_instance(factory):
    with patch("aws_testkit.src.clients.boto3.client") as mock_boto:
        mock_instance = MagicMock()
        mock_boto.return_value = mock_instance
        c1 = factory.get_client("s3")
        c2 = factory.get_client("s3")
        mock_boto.assert_called_once_with("s3", region_name="us-east-1")
        assert c1 is c2


def test_get_client_multiple_services(factory):
    with patch("aws_testkit.src.clients.boto3.client") as mock_boto:
        mock_instances = {"s3": MagicMock(), "ec2": MagicMock()}
        mock_boto.side_effect = lambda name, **_: mock_instances[name]
        s3 = factory.get_client("s3")
        ec2 = factory.get_client("ec2")
        assert s3 is mock_instances["s3"]
        assert ec2 is mock_instances["ec2"]
        assert mock_boto.call_count == 2


def test_close_clients_no_close_method(factory):
    no_close_client = object()  # não tem .close()
    factory._sync_clients["s3"] = no_close_client
    # Deve apenas remover do cache, sem erro
    factory.close_clients()
    assert "s3" not in factory._sync_clients


@pytest.mark.asyncio
async def test_get_async_client_returns_same_instance(factory):
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
async def test_close_async_clients_calls_aexit(factory):
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aexit__ = AsyncMock()
    factory._async_clients["s3"] = (MagicMock(), mock_cm, mock_client)
    await factory.close_async_clients()
    mock_cm.__aexit__.assert_awaited_once_with(None, None, None)
    assert "s3" not in factory._async_clients


@pytest.mark.asyncio
async def test_close_async_clients_with_exception(factory):
    mock_client = AsyncMock()
    mock_cm = AsyncMock()
    mock_cm.__aexit__ = AsyncMock(side_effect=RuntimeError("fail"))
    factory._async_clients["s3"] = (MagicMock(), mock_cm, mock_client)
    # Mesmo com erro, deve remover do cache
    await factory.close_async_clients()
    assert "s3" not in factory._async_clients


@pytest.mark.asyncio
async def test_get_async_client_handles_aenter_exception(factory):
    mock_cm = AsyncMock()
    mock_cm.__aenter__.side_effect = RuntimeError("fail")
    mock_cm.__aexit__ = AsyncMock()
    with patch("aws_testkit.src.clients.aioboto3.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session.client.return_value = mock_cm
        mock_session_cls.return_value = mock_session
        with pytest.raises(RuntimeError):
            await factory.get_async_client("s3")
        mock_cm.__aexit__.assert_awaited_once_with(None, None, None)


def test_close_clients_empty_cache(factory):
    # Não deve lançar erro mesmo com cache vazio
    factory.close_clients()


@pytest.mark.asyncio
async def test_close_async_clients_empty_cache(factory):
    # Não deve lançar erro mesmo com cache vazio
    await factory.close_async_clients()

import asyncio
import unittest
from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock, patch

from src import ClientFactory


class TestClientFactory(unittest.TestCase):

    def setUp(self):
        self.factory = ClientFactory(region="us-east-1")

    def test_get_client_retorna_mesma_instancia(self):
        with patch("src.clients.boto3.client") as mock_boto:
            mock_instance = MagicMock()
            mock_boto.return_value = mock_instance

            c1 = self.factory.get_client("s3")
            c2 = self.factory.get_client("s3")

            mock_boto.assert_called_once_with("s3", region_name="us-east-1")
            self.assertIs(c1, c2)

    def test_get_client_multiplos_servicos(self):
        with patch("src.clients.boto3.client") as mock_boto:
            instancias = {"s3": MagicMock(), "ec2": MagicMock()}
            mock_boto.side_effect = lambda nome, **_: instancias[nome]

            s3 = self.factory.get_client("s3")
            ec2 = self.factory.get_client("ec2")

            self.assertIs(s3, instancias["s3"])
            self.assertIs(ec2, instancias["ec2"])
            self.assertEqual(mock_boto.call_count, 2)

    def test_close_clients_com_metodo_close(self):
        mock_client = MagicMock()
        self.factory._sync_clients["s3"] = mock_client

        self.factory.close_clients()

        mock_client.close.assert_called_once()
        self.assertNotIn("s3", self.factory._sync_clients)

    def test_close_clients_sem_metodo_close(self):
        self.factory._sync_clients["s3"] = object()  # sem close()
        # Não deve gerar erro
        self.factory.close_clients()
        self.assertNotIn("s3", self.factory._sync_clients)

    def test_close_clients_cache_vazio(self):
        # Deve rodar sem erro mesmo sem nada no cache
        self.factory.close_clients()

    def test_close_async_clients_cache_vazio(self):
        asyncio.run(self.factory.close_async_clients())

    def test_close_async_clients_com_aexit(self):
        mock_client = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aexit__ = AsyncMock()
        self.factory._async_clients["s3"] = (MagicMock(), mock_cm, mock_client)

        asyncio.run(self.factory.close_async_clients())

        mock_cm.__aexit__.assert_awaited_once_with(None, None, None)
        self.assertNotIn("s3", self.factory._async_clients)

    def test_close_async_clients_com_excecao_no_aexit(self):
        mock_client = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aexit__ = AsyncMock(side_effect=RuntimeError("falha"))
        self.factory._async_clients["s3"] = (MagicMock(), mock_cm, mock_client)

        asyncio.run(self.factory.close_async_clients())
        # Mesmo com erro, deve remover do cache
        self.assertNotIn("s3", self.factory._async_clients)

    def test_get_async_client_retorna_mesma_instancia(self):
        mock_client = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_client

        with patch("src.clients.aioboto3.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.client.return_value = mock_cm
            mock_session_cls.return_value = mock_session

            c1 = asyncio.run(self.factory.get_async_client("s3"))
            c2 = asyncio.run(self.factory.get_async_client("s3"))

            mock_session.client.assert_called_once_with("s3", region_name="us-east-1")
            self.assertIs(c1, c2)

    def test_get_async_client_com_erro_no_aenter(self):
        mock_cm = AsyncMock()
        mock_cm.__aenter__.side_effect = RuntimeError("falha")
        mock_cm.__aexit__ = AsyncMock()

        with patch("src.clients.aioboto3.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.client.return_value = mock_cm
            mock_session_cls.return_value = mock_session

            with self.assertRaises(RuntimeError):
                asyncio.run(self.factory.get_async_client("s3"))

            mock_cm.__aexit__.assert_awaited_once_with(None, None, None)


if __name__ == "__main__":
    unittest.main()

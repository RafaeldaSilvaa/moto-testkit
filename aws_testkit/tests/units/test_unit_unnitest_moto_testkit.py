import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from aws_testkit.src import ClientFactory


class TestClientFactory(unittest.TestCase):

    def setUp(self):
        self.factory = ClientFactory(region="us-east-1")

    def test_get_client_returns_same_instance(self):
        with patch("aws_testkit.src.clients.boto3.client") as mock_boto:
            mock_instance = MagicMock()
            mock_boto.return_value = mock_instance

            c1 = self.factory.get_client("s3")
            c2 = self.factory.get_client("s3")

            mock_boto.assert_called_once_with("s3", region_name="us-east-1")
            self.assertIs(c1, c2)

    def test_get_client_multiple_services(self):
        with patch("aws_testkit.src.clients.boto3.client") as mock_boto:
            mock_instances = {"s3": MagicMock(), "ec2": MagicMock()}
            mock_boto.side_effect = lambda name, **_: mock_instances[name]

            s3 = self.factory.get_client("s3")
            ec2 = self.factory.get_client("ec2")

            self.assertIs(s3, mock_instances["s3"])
            self.assertIs(ec2, mock_instances["ec2"])
            self.assertEqual(mock_boto.call_count, 2)

    def test_close_clients_no_close_method(self):
        self.factory._sync_clients["s3"] = object()  # não tem .close()
        # Não deve lançar erro
        self.factory.close_clients()
        self.assertNotIn("s3", self.factory._sync_clients)

    def test_close_clients_calls_close(self):
        mock_client = MagicMock()
        self.factory._sync_clients["s3"] = mock_client

        self.factory.close_clients()

        mock_client.close.assert_called_once()
        self.assertNotIn("s3", self.factory._sync_clients)

    def test_close_clients_empty_cache(self):
        # Cache vazio, não deve falhar
        self.factory.close_clients()

    def test_close_async_clients_empty_cache(self):
        asyncio.run(self.factory.close_async_clients())

    def test_close_async_clients_with_exception(self):
        mock_client = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aexit__ = AsyncMock(side_effect=RuntimeError("fail"))
        self.factory._async_clients["s3"] = (MagicMock(), mock_cm, mock_client)

        asyncio.run(self.factory.close_async_clients())
        self.assertNotIn("s3", self.factory._async_clients)

    def test_close_async_clients_calls_aexit(self):
        mock_client = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aexit__ = AsyncMock()
        self.factory._async_clients["s3"] = (MagicMock(), mock_cm, mock_client)

        asyncio.run(self.factory.close_async_clients())

        mock_cm.__aexit__.assert_awaited_once_with(None, None, None)
        self.assertNotIn("s3", self.factory._async_clients)

    def test_get_async_client_returns_same_instance(self):
        mock_client = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_client

        with patch("aws_testkit.src.clients.aioboto3.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.client.return_value = mock_cm
            mock_session_cls.return_value = mock_session

            c1 = asyncio.run(self.factory.get_async_client("s3"))
            c2 = asyncio.run(self.factory.get_async_client("s3"))

            mock_session.client.assert_called_once_with("s3", region_name="us-east-1")
            self.assertIs(c1, c2)

    def test_get_async_client_handles_aenter_exception(self):
        mock_cm = AsyncMock()
        mock_cm.__aenter__.side_effect = RuntimeError("fail")
        mock_cm.__aexit__ = AsyncMock()

        with patch("aws_testkit.src.clients.aioboto3.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.client.return_value = mock_cm
            mock_session_cls.return_value = mock_session

            with self.assertRaises(RuntimeError):
                asyncio.run(self.factory.get_async_client("s3"))

            mock_cm.__aexit__.assert_awaited_once_with(None, None, None)


if __name__ == "__main__":
    unittest.main()

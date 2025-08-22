import threading
import asyncio
from typing import Any, Dict, Tuple
from contextlib import suppress
from botocore.client import BaseClient
import boto3
import aioboto3


class ClientFactory:
    """Gerencia criação e cache de boto3/aioboto3 clients de forma thread-safe e async-safe."""

    def __init__(self, region: str) -> None:
        self.region: str = region
        self._sync_clients: Dict[str, BaseClient] = {}
        self._async_clients: Dict[
            str,
            Tuple[aioboto3.Session, Any, BaseClient]
        ] = {}
        self._lock = threading.RLock()
        self._async_lock = asyncio.Lock()

    def get_client(self, service_name: str) -> BaseClient:
        """Obtém (ou cria) um cliente síncrono boto3."""
        with self._lock:
            client = self._sync_clients.get(service_name)
            if not client:
                client = boto3.client(service_name, region_name=self.region)
                self._sync_clients[service_name] = client
            return client

    async def get_async_client(self, service_name: str) -> BaseClient:
        """Obtém (ou cria) um cliente assíncrono aioboto3."""
        async with self._async_lock:
            if service_name in self._async_clients:
                return self._async_clients[service_name][2]

            session = aioboto3.Session()
            client_cm = session.client(service_name, region_name=self.region)

            try:
                client = await client_cm.__aenter__()
            except Exception:
                # Garante que o gerenciador de contexto seja fechado caso falhe a entrada
                with suppress(Exception):
                    await client_cm.__aexit__(None, None, None)
                raise

            self._async_clients[service_name] = (session, client_cm, client)
            return client

    def close_clients(self) -> None:
        """Fecha todos os clientes boto3 criados."""
        with self._lock:
            for svc, client in list(self._sync_clients.items()):
                with suppress(Exception):
                    if hasattr(client, "close"):
                        client.close()
                self._sync_clients.pop(svc, None)

    async def close_async_clients(self) -> None:
        """Fecha todos os clientes aioboto3 criados."""
        async with self._async_lock:
            for svc, (_session, client_cm, _client) in list(self._async_clients.items()):
                with suppress(Exception):
                    await client_cm.__aexit__(None, None, None)
                self._async_clients.pop(svc, None)

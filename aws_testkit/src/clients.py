import threading
import asyncio
from typing import Any, Dict, Tuple
import boto3
import aioboto3

class ClientFactory:
    """Gerencia criação e cache de boto3/aioboto3 clients."""

    def __init__(self, region: str) -> None:
        self.region = region
        self._sync_clients: Dict[str, Any] = {}
        self._async_clients: Dict[str, Tuple[aioboto3.Session, Any, Any]] = {}
        self._lock = threading.RLock()
        self._async_lock = asyncio.Lock()

    def get_client(self, service_name: str) -> Any:
        with self._lock:
            if service_name not in self._sync_clients:
                self._sync_clients[service_name] = boto3.client(service_name, region_name=self.region)
            return self._sync_clients[service_name]

    async def get_async_client(self, service_name: str) -> Any:
        async with self._async_lock:
            if service_name in self._async_clients:
                return self._async_clients[service_name][2]
            session = aioboto3.Session()
            client_cm = session.client(service_name, region_name=self.region)
            client = await client_cm.__aenter__()
            self._async_clients[service_name] = (session, client_cm, client)
            return client

    def close_clients(self) -> None:
        with self._lock:
            for svc, client in list(self._sync_clients.items()):
                try:
                    if hasattr(client, "close"):
                        client.close()
                except Exception:
                    pass
                finally:
                    self._sync_clients.pop(svc, None)

    async def close_async_clients(self) -> None:
        async with self._async_lock:
            for svc, (_session, client_cm, _client) in list(self._async_clients.items()):
                try:
                    await client_cm.__aexit__(None, None, None)
                except Exception:
                    pass
                finally:
                    self._async_clients.pop(svc, None)

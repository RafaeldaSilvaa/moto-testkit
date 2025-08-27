import aioboto3
from typing import Optional, List


class EventBridgeAsyncRepository:
    def __init__(self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"):
        self.endpoint_url = endpoint_url
        self.region_name = region_name

    async def put_rule(self, name: str, event_pattern: str):
        async with aioboto3.Session().client(
            "events", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            return await client.put_rule(Name=name, EventPattern=event_pattern)

    async def list_rules(self) -> List[str]:
        async with aioboto3.Session().client(
            "events", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            resp = await client.list_rules()
            return [r["Name"] for r in resp.get("Rules", [])]

    async def put_events(self, entries: list):
        async with aioboto3.Session().client(
            "events", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            return await client.put_events(Entries=entries)

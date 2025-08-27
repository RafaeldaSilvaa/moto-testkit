from typing import List, Optional

import boto3


class EventBridgeRepository:
    def __init__(
        self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"
    ):
        self.client = boto3.client(
            "events", endpoint_url=endpoint_url, region_name=region_name
        )

    def put_rule(self, name: str, event_pattern: str):
        return self.client.put_rule(Name=name, EventPattern=event_pattern)

    def list_rules(self) -> List[str]:
        resp = self.client.list_rules()
        return [r["Name"] for r in resp.get("Rules", [])]

    def put_events(self, entries: list):
        return self.client.put_events(Entries=entries)

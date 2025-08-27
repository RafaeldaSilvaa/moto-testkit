import aioboto3
from typing import Optional


class CloudWatchLogsAsyncRepository:
    def __init__(self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"):
        self.endpoint_url = endpoint_url
        self.region_name = region_name

    async def create_log_group(self, log_group_name: str):
        async with aioboto3.Session().client(
            "logs", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            await client.create_log_group(logGroupName=log_group_name)

    async def create_log_stream(self, log_group_name: str, log_stream_name: str):
        async with aioboto3.Session().client(
            "logs", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            await client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)

    async def put_log_events(self, log_group_name: str, log_stream_name: str, messages: list):
        events = [{"timestamp": 123456789, "message": m} for m in messages]
        async with aioboto3.Session().client(
            "logs", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            return await client.put_log_events(
                logGroupName=log_group_name, logStreamName=log_stream_name, logEvents=events
            )

    async def describe_log_groups(self):
        async with aioboto3.Session().client(
            "logs", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            resp = await client.describe_log_groups()
            return resp.get("logGroups", [])

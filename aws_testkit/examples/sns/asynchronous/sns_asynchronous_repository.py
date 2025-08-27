import aioboto3
from typing import Optional, List


class SNSAsyncRepository:
    def __init__(self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"):
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.session = aioboto3.Session()

    async def create_topic(self, name: str) -> str:
        async with self.session.client("sns", endpoint_url=self.endpoint_url, region_name=self.region_name) as client:
            resp = await client.create_topic(Name=name)
            return resp["TopicArn"]

    async def list_topics(self) -> List[str]:
        async with self.session.client("sns", endpoint_url=self.endpoint_url, region_name=self.region_name) as client:
            resp = await client.list_topics()
            return [t["TopicArn"] for t in resp.get("Topics", [])]

    async def publish(self, topic_arn: str, message: str):
        async with self.session.client("sns", endpoint_url=self.endpoint_url, region_name=self.region_name) as client:
            return await client.publish(TopicArn=topic_arn, Message=message)

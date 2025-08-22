import boto3
from typing import Optional, List


class SNSRepository:
    def __init__(self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"):
        self.client = boto3.client("sns", endpoint_url=endpoint_url, region_name=region_name)

    def create_topic(self, name: str) -> str:
        return self.client.create_topic(Name=name)["TopicArn"]

    def list_topics(self) -> List[str]:
        resp = self.client.list_topics()
        return [t["TopicArn"] for t in resp.get("Topics", [])]

    def subscribe(self, topic_arn: str, protocol: str, endpoint: str):
        return self.client.subscribe(TopicArn=topic_arn, Protocol=protocol, Endpoint=endpoint)

    def publish(self, topic_arn: str, message: str):
        return self.client.publish(TopicArn=topic_arn, Message=message)

from typing import List, Optional

import boto3
from botocore.exceptions import ClientError


class SQSRepository:
    def __init__(
        self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"
    ):
        self.client = boto3.client(
            "sqs", endpoint_url=endpoint_url, region_name=region_name
        )

    def create_queue(self, queue_name: str) -> str:
        resp = self.client.create_queue(QueueName=queue_name)
        return resp["QueueUrl"]

    def list_queues(self) -> List[str]:
        resp = self.client.list_queues()
        return resp.get("QueueUrls", [])

    def send_message(self, queue_url: str, message_body: str):
        return self.client.send_message(QueueUrl=queue_url, MessageBody=message_body)

    def receive_messages(self, queue_url: str, max_number: int = 1) -> List[dict]:
        resp = self.client.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=max_number
        )
        return resp.get("Messages", [])

    def delete_message(self, queue_url: str, receipt_handle: str):
        self.client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

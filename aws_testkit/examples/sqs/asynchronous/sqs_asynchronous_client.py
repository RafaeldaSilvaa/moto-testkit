import aioboto3
from typing import Optional, Dict, Any, List


class SQSAsyncClient:
    """
    Uma classe para interagir de forma assíncrona com o Amazon SQS.
    """

    def __init__(self, region_name: str, queue_url: str):
        self.region_name = region_name
        self.queue_url = queue_url

    async def send_message(
        self, message_body: str, message_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        async with aioboto3.Session().client("sqs", region_name=self.region_name) as sqs:
            return await sqs.send_message(
                QueueUrl=self.queue_url, MessageBody=message_body, MessageAttributes=message_attributes or {}
            )

    async def receive_messages(
        self, max_number_of_messages: int = 10, wait_time_seconds: int = 20
    ) -> List[Dict[str, Any]]:
        async with aioboto3.Session().client("sqs", region_name=self.region_name) as sqs:
            response = await sqs.receive_message(
                QueueUrl=self.queue_url, MaxNumberOfMessages=max_number_of_messages, WaitTimeSeconds=wait_time_seconds
            )
            return response.get("Messages", [])

    async def delete_message(self, receipt_handle: str) -> Dict[str, Any]:
        async with aioboto3.Session().client("sqs", region_name=self.region_name) as sqs:
            return await sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=receipt_handle)

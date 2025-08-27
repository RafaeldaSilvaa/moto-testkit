# helpers.py
from __future__ import annotations

import io
from typing import Any, Dict

from pydantic import BaseModel, Field

from .clients import ClientFactory


# ---------------- Models (Pydantic v1) ----------------
class S3ObjectModel(BaseModel):
    bucket: str = Field(..., min_length=1)
    key: str = Field(..., min_length=1)
    body: bytes


class DynamoItemModel(BaseModel):
    table: str = Field(..., min_length=1)
    item: Dict[str, Any]


class SQSMessageModel(BaseModel):
    queue_url: str = Field(..., min_length=1)
    body: str


# ---------------- Helpers (dependem de ClientFactory) ----------------
class S3HelperTyped:
    def __init__(self, clients: ClientFactory) -> None:
        self._clients = clients

    # synchronous
    def create_bucket(self, bucket: str) -> Dict[str, Any]:
        client = self._clients.get_client("s3")
        return client.create_bucket(Bucket=bucket)

    def put_object(self, model: S3ObjectModel) -> Dict[str, Any]:
        client = self._clients.get_client("s3")
        return client.put_object(Bucket=model.bucket, Key=model.key, Body=model.body)

    def get_object_body(self, bucket: str, key: str) -> bytes:
        client = self._clients.get_client("s3")
        resp = client.get_object(Bucket=bucket, Key=key)
        return resp["Body"].read()

    # asynchronous
    async def put_object_async(self, model: S3ObjectModel):
        client = await self._clients.get_async_client("s3")

        body_data = model.body
        # 🚑 Contorno: moto + aiobotocore → garante que é BytesIO
        if isinstance(body_data, (bytes, bytearray)):
            body_data = io.BytesIO(body_data)

        return await client.put_object(
            Bucket=model.bucket, Key=model.key, Body=body_data
        )

    async def get_object_body_async(self, bucket: str, key: str) -> bytes:
        client = await self._clients.get_async_client("s3")
        resp = await client.get_object(Bucket=bucket, Key=key)
        return await resp["Body"].read()


class DynamoHelperTyped:
    def __init__(self, clients: ClientFactory) -> None:
        self._clients = clients

    def create_table(self, table: str, key_name: str = "id") -> Dict[str, Any]:
        client = self._clients.get_client("dynamodb")
        return client.create_table(
            TableName=table,
            KeySchema=[{"AttributeName": key_name, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": key_name, "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

    def put_item(self, model: DynamoItemModel) -> Dict[str, Any]:
        client = self._clients.get_client("dynamodb")
        return client.put_item(TableName=model.table, Item=model.item)

    def get_item(self, table: str, key: dict) -> Dict[str, Any]:
        client = self._clients.get_client("dynamodb")
        return client.get_item(TableName=table, Key=key)

    async def put_item_async(self, model: DynamoItemModel) -> Dict[str, Any]:
        client = await self._clients.get_async_client("dynamodb")
        return await client.put_item(TableName=model.table, Item=model.item)

    async def get_item_async(self, table: str, key: dict) -> Dict[str, Any]:
        client = await self._clients.get_async_client("dynamodb")
        return await client.get_item(TableName=table, Key=key)


class SQSHelperTyped:
    def __init__(self, clients: ClientFactory) -> None:
        self._clients = clients

    def create_queue(self, name: str) -> Dict[str, Any]:
        client = self._clients.get_client("sqs")
        return client.create_queue(QueueName=name)

    def send_message(self, model: SQSMessageModel) -> Dict[str, Any]:
        client = self._clients.get_client("sqs")
        return client.send_message(QueueUrl=model.queue_url, MessageBody=model.body)

    def receive_messages(self, queue_url: str, max_num: int = 1) -> Dict[str, Any]:
        client = self._clients.get_client("sqs")
        return client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=max_num)

    async def send_message_async(self, model: SQSMessageModel) -> Dict[str, Any]:
        client = await self._clients.get_async_client("sqs")
        return await client.send_message(
            QueueUrl=model.queue_url, MessageBody=model.body
        )

    async def receive_messages_async(
        self, queue_url: str, max_num: int = 1
    ) -> Dict[str, Any]:
        client = await self._clients.get_async_client("sqs")
        return await client.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=max_num
        )

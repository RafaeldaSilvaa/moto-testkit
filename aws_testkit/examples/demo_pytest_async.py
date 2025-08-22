import pytest
from aws_testkit.src.moto_testkit import MotoTestKit
import aioboto3


@pytest.mark.asyncio
async def test_dynamo_sqs_s3_with_moto():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    try:
        # --- DynamoDB ---
        dynamo_client = await kit.get_async_client("dynamodb")
        await dynamo_client.create_table(
            TableName="Users",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        await dynamo_client.put_item(
            TableName="Users",
            Item={"id": {"S": "123"}, "name": {"S": "Alice"}}
        )
        resp = await dynamo_client.get_item(
            TableName="Users",
            Key={"id": {"S": "123"}}
        )
        assert resp["Item"]["name"]["S"] == "Alice"

        # --- SQS ---
        sqs_client = await kit.get_async_client("sqs")
        queue = await sqs_client.create_queue(QueueName="test-queue")
        queue_url = queue["QueueUrl"]

        await sqs_client.send_message(QueueUrl=queue_url, MessageBody="Hello SQS")
        msgs = await sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        assert msgs["Messages"][0]["Body"] == "Hello SQS"

        # --- S3 ---
        s3_client = kit.get_client("s3")
        s3_client.create_bucket(Bucket="my-bucket")
        s3_client.put_object(Bucket="my-bucket", Key="file.txt", Body=b"content")
        obj = s3_client.get_object(Bucket="my-bucket", Key="file.txt")
        body = obj["Body"].read()
        assert body == b"content"

    finally:
        await kit.close_async_clients()
        kit.stop()

import io

import pytest
from aws_testkit.src.moto_testkit import AutoMotoTestKit

@pytest.mark.asyncio
async def test_all_services_with_auto_moto():
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
        # DynamoDB
        dynamo = await kit.get_async_client("dynamodb")
        await dynamo.create_table(
            TableName="Products",
            KeySchema=[{"AttributeName": "sku", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "sku", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        await dynamo.put_item(
            TableName="Products",
            Item={"sku": {"S": "ABC"}, "price": {"N": "19.99"}}
        )
        resp = await dynamo.get_item(
            TableName="Products",
            Key={"sku": {"S": "ABC"}}
        )
        assert resp["Item"]["price"]["N"] == "19.99"

        # SQS
        sqs = await kit.get_async_client("sqs")
        q = await sqs.create_queue(QueueName="orders")
        q_url = q["QueueUrl"]
        await sqs.send_message(QueueUrl=q_url, MessageBody="order-1")
        msgs = await sqs.receive_message(QueueUrl=q_url)
        assert msgs["Messages"][0]["Body"] == "order-1"

        # S3
        s3 = kit.get_client("s3")
        s3.create_bucket(Bucket="assets")
        s3.put_object(Bucket="assets", Key="img.png", Body=io.BytesIO(b"fake-image"))
        obj = s3.get_object(Bucket="assets", Key="img.png")
        data = obj["Body"].read()
        assert data == b"fake-image"

import pytest

from src.helpers import (DynamoItemModel, S3ObjectModel,
                                     SQSMessageModel)
from src.moto_testkit import AutoMotoTestKit, MotoTestKit

AWS_REGION = "us-east-1"


@pytest.fixture
def moto_testkit():
    testkit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield testkit
    testkit.close_clients()
    testkit.stop()


# -------- SYNC --------
def test_sync_s3_dynamo_sqs(moto_testkit):
    # S3
    s3_helper = moto_testkit.s3_helper()
    s3_helper.create_bucket("bucket_sync")
    s3_helper.put_object(
        S3ObjectModel(bucket="bucket_sync", key="file.txt", body=b"abc")
    )
    assert s3_helper.get_object_body("bucket_sync", "file.txt") == b"abc"

    # DynamoDB
    dynamo_helper = moto_testkit.dynamo_helper()
    dynamo_helper.create_table("users_table", key_name="id")
    dynamo_helper.put_item(
        DynamoItemModel(
            table="users_table", item={"id": {"S": "1"}, "name": {"S": "Bob"}}
        )
    )
    assert (
        dynamo_helper.get_item("users_table", {"id": {"S": "1"}})["Item"]["name"]["S"]
        == "Bob"
    )

    # SQS
    sqs_helper = moto_testkit.sqs_helper()
    created_queue = sqs_helper.create_queue("queue_sync")
    sqs_helper.send_message(
        SQSMessageModel(queue_url=created_queue["QueueUrl"], body="hello")
    )
    received_messages = sqs_helper.receive_messages(created_queue["QueueUrl"])
    assert received_messages["Messages"][0]["Body"] == "hello"


# -------- ASYNC --------
@pytest.mark.asyncio
async def test_async_s3_dynamo_sqs(moto_testkit):
    # S3
    s3_helper = moto_testkit.s3_helper()
    s3_helper.create_bucket("bucket")
    s3_helper.put_object(
        S3ObjectModel(bucket="bucket", key="async.txt", body=b"xyz")
    )
    assert s3_helper.get_object_body("bucket", "async.txt") == b"xyz"

    # DynamoDB
    dynamo_helper = moto_testkit.dynamo_helper()
    dynamo_helper.create_table("products_table", key_name="sku")
    await dynamo_helper.put_item_async(
        DynamoItemModel(
            table="products_table", item={"sku": {"S": "P1"}, "price": {"N": "9"}}
        )
    )
    product_item = await dynamo_helper.get_item_async(
        "products_table", {"sku": {"S": "P1"}}
    )
    assert product_item["Item"]["price"]["N"] == "9"

    # SQS
    sqs_helper = moto_testkit.sqs_helper()
    created_queue = sqs_helper.create_queue("queue_async")
    await sqs_helper.send_message_async(
        SQSMessageModel(queue_url=created_queue["QueueUrl"], body="world")
    )
    received_messages = await sqs_helper.receive_messages_async(
        created_queue["QueueUrl"]
    )
    assert received_messages["Messages"][0]["Body"] == "world"


# -------- CONTEXT MANAGER --------
@pytest.mark.asyncio
async def test_auto_moto_all_services():
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as auto_testkit:
        s3_helper = auto_testkit.s3_helper()
        s3_helper.create_bucket("bucket_ctx")
        s3_helper.put_object(
            S3ObjectModel(bucket="bucket_ctx", key="ctx_key", body=b"img")
        )
        assert s3_helper.get_object_body("bucket_ctx", "ctx_key") == b"img"

        dynamo_helper = auto_testkit.dynamo_helper()
        dynamo_helper.create_table("ctx_table", key_name="id")
        await dynamo_helper.put_item_async(
            DynamoItemModel(table="ctx_table", item={"id": {"S": "1"}})
        )
        assert "Item" in await dynamo_helper.get_item_async(
            "ctx_table", {"id": {"S": "1"}}
        )

        sqs_helper = auto_testkit.sqs_helper()
        created_queue = sqs_helper.create_queue("queue_ctx")
        await sqs_helper.send_message_async(
            SQSMessageModel(queue_url=created_queue["QueueUrl"], body="o1")
        )
        received_messages = await sqs_helper.receive_messages_async(
            created_queue["QueueUrl"]
        )
        assert received_messages["Messages"][0]["Body"] == "o1"

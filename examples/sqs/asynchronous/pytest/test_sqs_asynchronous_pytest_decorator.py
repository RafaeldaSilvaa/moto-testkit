import asyncio

import pytest

from examples.sqs.asynchronous.sqs_asynchronous_client import \
    SQSAsyncClient
from src.moto_testkit import AutoMotoTestKit, use_moto_testkit

AWS_REGION = "us-east-1"
QUEUE_NAME = "fila-teste"


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_sqs_basic_flow_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    sqs_client = moto_testkit.get_client("sqs")
    queue = sqs_client.create_queue(QueueName="test-queue")
    queue_url = queue["QueueUrl"]

    my_sqs = SQSAsyncClient(region_name=moto_testkit.region, queue_url=queue_url)
    send_resp = await my_sqs.send_message("Hello MotoTestKit!")
    assert "MessageId" in send_resp

    messages = await my_sqs.receive_messages()
    assert len(messages) == 1
    assert messages[0]["Body"] == "Hello MotoTestKit!"

    receipt_handle = messages[0]["ReceiptHandle"]
    del_resp = await my_sqs.delete_message(receipt_handle)
    assert del_resp["ResponseMetadata"]["HTTPStatusCode"] == 200


@pytest.mark.asyncio
@use_moto_testkit(auto_start=True, patch_aiobotocore=True)
async def test_sqs_send_receive_delete_with_decorator(
    moto_testkit: AutoMotoTestKit,
) -> None:
    sqs_client_boto = await moto_testkit.get_async_client("sqs")
    create_resp = await sqs_client_boto.create_queue(QueueName=QUEUE_NAME)
    queue_url = create_resp["QueueUrl"]

    sqs_client = SQSAsyncClient(region_name=AWS_REGION, queue_url=queue_url)
    message_to_send = "Mensagem de teste via pytest + Moto"
    await sqs_client.send_message(message_to_send)
    await asyncio.sleep(0.1)

    messages = await sqs_client.receive_messages()
    assert messages
    for message in messages:
        assert message["Body"] == message_to_send
        await sqs_client.delete_message(message["ReceiptHandle"])

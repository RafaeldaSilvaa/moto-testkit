import pytest

from aws_testkit.examples.sqs.assincrono.sqs_client import SQSAsyncClient
from aws_testkit.src.moto_testkit import AutoMotoTestKit



@pytest.mark.asyncio
async def test_sqs():
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
        # cria fila fake
        sqs_client = kit.get_client("sqs")
        queue = sqs_client.create_queue(QueueName="test-queue")
        queue_url = queue["QueueUrl"]

        # usa o cliente real
        my_sqs = SQSAsyncClient(region_name=kit.region, queue_url=queue_url)

        # envia mensagem
        send_resp = await my_sqs.send_message("Hello MotoTestKit!")
        assert "MessageId" in send_resp

        # recebe mensagem
        messages = await my_sqs.receive_messages()
        assert len(messages) == 1
        assert messages[0]["Body"] == "Hello MotoTestKit!"

        # deleta mensagem
        receipt_handle = messages[0]["ReceiptHandle"]
        del_resp = await my_sqs.delete_message(receipt_handle)
        assert del_resp["ResponseMetadata"]["HTTPStatusCode"] == 200

import pytest
import asyncio

AWS_REGION = "us-east-1"
QUEUE_NAME = "fila-teste"

@pytest.mark.asyncio
async def test_sqs_send_receive_delete_with_moto():
    async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
        # Cria cliente SQS mockado
        sqs_client_boto = await kit.get_async_client("sqs")

        # Cria fila mockada
        create_resp = await sqs_client_boto.create_queue(QueueName=QUEUE_NAME)
        queue_url = create_resp["QueueUrl"]

        # Usa o SQSAsyncClient apontando para o mock
        sqs_client = SQSAsyncClient(region_name=AWS_REGION, queue_url=queue_url)

        # Envia mensagem
        message_to_send = "Mensagem de teste via pytest + Moto"
        await sqs_client.send_message(message_to_send)
        await asyncio.sleep(0.1)  # pequeno delay para simulação

        # Recebe mensagens
        messages = await sqs_client.receive_messages()
        assert messages, "Nenhuma mensagem recebida"

        # Verifica conteúdo e exclui
        for message in messages:
            assert message["Body"] == message_to_send
            await sqs_client.delete_message(message["ReceiptHandle"])

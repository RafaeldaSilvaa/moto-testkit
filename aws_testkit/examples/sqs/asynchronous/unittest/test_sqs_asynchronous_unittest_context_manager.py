import unittest
from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestSQSRepositoryWithContextManager(unittest.IsolatedAsyncioTestCase):
    async def test_sqs_queue_creation_and_listing(self) -> None:
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
            sqs_client = await moto_testkit.get_async_client("sqs")
            queue_name = "minha-fila-teste"
            await sqs_client.create_queue(QueueName=queue_name)
            response = await sqs_client.list_queues()
            queue_urls = response.get("QueueUrls", [])
            self.assertTrue(any(queue_name in url for url in queue_urls))

    async def test_sqs_send_and_receive_message(self) -> None:
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as moto_testkit:
            sqs_client = await moto_testkit.get_async_client("sqs")
            queue_name = "fila-mensagens"
            create_resp = await sqs_client.create_queue(QueueName=queue_name)
            queue_url = create_resp["QueueUrl"]

            await sqs_client.send_message(QueueUrl=queue_url, MessageBody="Olá, mundo!")
            recv_resp = await sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
            messages = recv_resp.get("Messages", [])
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["Body"], "Olá, mundo!")

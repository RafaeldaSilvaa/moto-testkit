import unittest
from aws_testkit.src.moto_testkit import AutoMotoTestKit, use_moto_testkit


class TestSQSRepositoryWithDecorator(unittest.IsolatedAsyncioTestCase):
    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_sqs_queue_creation_and_listing(self, moto_testkit: AutoMotoTestKit) -> None:
        sqs_client = await moto_testkit.get_async_client("sqs")
        queue_name = "minha-fila-teste"
        await sqs_client.create_queue(QueueName=queue_name)
        response = await sqs_client.list_queues()
        queue_urls = response.get("QueueUrls", [])
        self.assertTrue(any(queue_name in url for url in queue_urls))

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_sqs_send_and_receive_message(self, moto_testkit: AutoMotoTestKit) -> None:
        sqs_client = await moto_testkit.get_async_client("sqs")
        queue_name = "fila-mensagens"
        create_resp = await sqs_client.create_queue(QueueName=queue_name)
        queue_url = create_resp["QueueUrl"]

        await sqs_client.send_message(QueueUrl=queue_url, MessageBody="Olá, mundo!")
        recv_resp = await sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
        messages = recv_resp.get("Messages", [])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["Body"], "Olá, mundo!")

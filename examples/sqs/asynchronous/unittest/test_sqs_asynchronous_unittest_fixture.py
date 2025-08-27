import unittest

from src.moto_testkit import MotoTestKit


class TestSQSRepositoryFixtureMotoTestKit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(
            auto_start=True, patch_aiobotocore=True
        )

    async def asyncTearDown(self) -> None:
        await self.moto_testkit.close_async_clients()
        self.moto_testkit.stop()

    async def test_sqs_queue_creation_and_listing(self) -> None:
        sqs_client = await self.moto_testkit.get_async_client("sqs")
        queue_name = "minha-fila-teste"
        await sqs_client.create_queue(QueueName=queue_name)
        response = await sqs_client.list_queues()
        queue_urls = response.get("QueueUrls", [])
        self.assertTrue(any(queue_name in url for url in queue_urls))

    async def test_sqs_send_and_receive_message(self) -> None:
        sqs_client = await self.moto_testkit.get_async_client("sqs")
        queue_name = "fila-mensagens"
        create_resp = await sqs_client.create_queue(QueueName=queue_name)
        queue_url = create_resp["QueueUrl"]

        await sqs_client.send_message(QueueUrl=queue_url, MessageBody="Olá, mundo!")
        recv_resp = await sqs_client.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=1
        )
        messages = recv_resp.get("Messages", [])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["Body"], "Olá, mundo!")

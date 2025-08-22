import unittest
from aws_testkit.src.moto_testkit import MotoTestKit, AutoMotoTestKit


class TestSQSWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Inicia o MotoTestKit antes de cada teste
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    async def asyncTearDown(self):
        # Fecha e para o MotoTestKit automaticamente
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_sqs_queue_creation_and_listing(self):
        # Cria um cliente SQS assíncrono
        sqs_client = await self.kit.get_async_client("sqs")

        # Cria uma fila
        queue_name = "minha-fila-teste"
        await sqs_client.create_queue(QueueName=queue_name)

        # Lista filas e verifica se a criada está presente
        response = await sqs_client.list_queues()
        queue_urls = response.get("QueueUrls", [])

        self.assertTrue(
            any(queue_name in url for url in queue_urls),
            f"A fila '{queue_name}' não foi encontrada na lista."
        )

    async def test_sqs_send_and_receive_message(self):
        sqs_client = await self.kit.get_async_client("sqs")

        # Cria fila
        queue_name = "fila-mensagens"
        create_resp = await sqs_client.create_queue(QueueName=queue_name)
        queue_url = create_resp["QueueUrl"]

        # Envia mensagem
        await sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody="Olá, mundo!"
        )

        # Recebe mensagem
        recv_resp = await sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1
        )

        messages = recv_resp.get("Messages", [])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["Body"], "Olá, mundo!")


class TestSQSWithContext(unittest.IsolatedAsyncioTestCase):
    async def test_sqs_with_context_manager(self):
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
            sqs_client = await kit.get_async_client("sqs")
            await sqs_client.create_queue(QueueName="fila-contexto")
            resp = await sqs_client.list_queues()
            self.assertIn("fila-contexto", str(resp))

    async def test_two_separate_environments(self):
        # Primeiro ambiente
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit1:
            sqs1 = await kit1.get_async_client("sqs")
            await sqs1.create_queue(QueueName="fila-1")
            resp1 = await sqs1.list_queues()
            self.assertIn("fila-1", str(resp1))

        # Segundo ambiente, completamente limpo
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit2:
            sqs2 = await kit2.get_async_client("sqs")
            resp2 = await sqs2.list_queues()
            self.assertNotIn("fila-1", str(resp2))

if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()

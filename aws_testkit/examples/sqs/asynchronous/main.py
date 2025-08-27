import asyncio

from aws_testkit.examples.sqs.asynchronous.sqs_asynchronous_client import SQSAsyncClient

# Configurações da AWS - Substitua pelos seus valores
AWS_REGION = "sua-regiao-aws"
SQS_QUEUE_URL = "https://sqs.sua-regiao-aws.amazonaws.com/123456789012/seu-nome-de-fila"


async def main():
    """
    Função principal para demonstrar o uso do SQSAsyncClient.
    """
    sqs_client = SQSAsyncClient(region_name=AWS_REGION, queue_url=SQS_QUEUE_URL)

    # 1. Enviar uma mensagem
    print("--- Enviando mensagem ---")
    message_to_send = "Esta é uma mensagem de teste enviada de forma assíncrona."
    await sqs_client.send_message(message_to_send)
    await asyncio.sleep(2)  # Atraso para garantir que a mensagem esteja disponível na fila

    # 2. Receber mensagens
    print("\n--- Recebendo mensagens ---")
    messages = await sqs_client.receive_messages()

    if messages:
        for message in messages:
            print(f"Mensagem recebida: {message['Body']}")
            receipt_handle = message["ReceiptHandle"]

            # 3. Excluir a mensagem após o processamento
            print(f"Excluindo mensagem com ReceiptHandle: {receipt_handle}")
            await sqs_client.delete_message(receipt_handle)
    else:
        print("Não há mensagens para processar.")


if __name__ == "__main__":
    # Garante que o loop de eventos seja executado
    asyncio.run(main())

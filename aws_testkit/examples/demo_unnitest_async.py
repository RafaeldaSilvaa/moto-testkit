import unittest
from aws_testkit.src.moto_testkit import MotoTestKit

AWS_REGION = "us-east-1"

class TestAWSWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Inicia o MotoTestKit antes de cada teste
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

        # Cria clientes assíncronos para cada serviço
        self.dynamo = await self.kit.get_async_client("dynamodb")
        self.sqs = await self.kit.get_async_client("sqs")
        self.s3 = self.kit.get_client("s3")

    async def asyncTearDown(self):
        # Fecha todos os clientes e para o Moto
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_dynamodb(self):
        await self.dynamo.create_table(
            TableName="Users",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        await self.dynamo.put_item(
            TableName="Users",
            Item={"id": {"S": "1"}, "name": {"S": "Alice"}}
        )
        resp = await self.dynamo.get_item(
            TableName="Users",
            Key={"id": {"S": "1"}}
        )
        self.assertEqual(resp["Item"]["name"]["S"], "Alice")

    async def test_sqs(self):
        q = await self.sqs.create_queue(QueueName="queue1")
        q_url = q["QueueUrl"]
        await self.sqs.send_message(QueueUrl=q_url, MessageBody="msg1")
        msgs = await self.sqs.receive_message(QueueUrl=q_url)
        self.assertEqual(msgs["Messages"][0]["Body"], "msg1")

    async def test_s3(self):
        self.s3.create_bucket(Bucket="bucket1")
        self.s3.put_object(Bucket="bucket1", Key="file.txt", Body=b"abc")
        obj = self.s3.get_object(Bucket="bucket1", Key="file.txt")
        data = obj["Body"].read()
        self.assertEqual(data, b"abc")

if __name__ == "__main__":
    unittest.main()

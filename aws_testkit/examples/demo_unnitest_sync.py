import unittest
from aws_testkit.src.moto_testkit import MotoTestKit

AWS_REGION = "us-east-1"

class TestAWSWithMotoSync(unittest.TestCase):
    def setUp(self):
        # Inicia o MotoTestKit
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=False)

        # Cria clientes síncronos
        self.dynamo = self.kit.get_client("dynamodb")
        self.sqs = self.kit.get_client("sqs")
        self.s3 = self.kit.get_client("s3")

    def tearDown(self):
        # Fecha clientes e para o Moto
        self.kit.close_clients()
        self.kit.stop()

    def test_dynamodb(self):
        self.dynamo.create_table(
            TableName="Users",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST"
        )
        self.dynamo.put_item(
            TableName="Users",
            Item={"id": {"S": "1"}, "name": {"S": "Alice"}}
        )
        resp = self.dynamo.get_item(
            TableName="Users",
            Key={"id": {"S": "1"}}
        )
        self.assertEqual(resp["Item"]["name"]["S"], "Alice")

    def test_sqs(self):
        q = self.sqs.create_queue(QueueName="queue1")
        q_url = q["QueueUrl"]
        self.sqs.send_message(QueueUrl=q_url, MessageBody="msg1")
        msgs = self.sqs.receive_message(QueueUrl=q_url)
        self.assertEqual(msgs["Messages"][0]["Body"], "msg1")

    def test_s3(self):
        self.s3.create_bucket(Bucket="bucket1")
        self.s3.put_object(Bucket="bucket1", Key="file.txt", Body=b"abc")
        obj = self.s3.get_object(Bucket="bucket1", Key="file.txt")
        data = obj["Body"].read()
        self.assertEqual(data, b"abc")

if __name__ == "__main__":
    unittest.main()

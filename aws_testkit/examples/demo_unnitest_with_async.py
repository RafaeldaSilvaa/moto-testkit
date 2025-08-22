import unittest
import asyncio

from aws_testkit.src.moto_testkit import AutoMotoTestKit

AWS_REGION = "us-east-1"

class TestAWSWithAutoMoto(unittest.IsolatedAsyncioTestCase):
    async def test_dynamo_sqs_s3(self):
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
            # DynamoDB
            dynamo = await kit.get_async_client("dynamodb")
            await dynamo.create_table(
                TableName="Users",
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST"
            )
            await dynamo.put_item(
                TableName="Users",
                Item={"id": {"S": "1"}, "name": {"S": "Bob"}}
            )
            resp = await dynamo.get_item(
                TableName="Users",
                Key={"id": {"S": "1"}}
            )
            self.assertEqual(resp["Item"]["name"]["S"], "Bob")

            # SQS
            sqs = await kit.get_async_client("sqs")
            q = await sqs.create_queue(QueueName="queue1")
            q_url = q["QueueUrl"]
            await sqs.send_message(QueueUrl=q_url, MessageBody="msg1")
            msgs = await sqs.receive_message(QueueUrl=q_url)
            self.assertEqual(msgs["Messages"][0]["Body"], "msg1")

            # S3
            s3 = kit.get_client("s3")
            s3.create_bucket(Bucket="bucket1")
            s3.put_object(Bucket="bucket1", Key="file.txt", Body=b"abc")
            obj = s3.get_object(Bucket="bucket1", Key="file.txt")
            data = obj["Body"].read()
            self.assertEqual(data, b"abc")

if __name__ == "__main__":
    unittest.main()

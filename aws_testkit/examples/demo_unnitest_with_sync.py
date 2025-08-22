import unittest
from aws_testkit.src.moto_testkit import MotoTestKit, AutoMotoTestKit


class TestAWSWithAutoMotoSync(unittest.TestCase):
    def test_dynamo_sqs_s3(self):
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=False) as kit:
            # DynamoDB
            dynamo = kit.get_client("dynamodb")
            dynamo.create_table(
                TableName="Users",
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST"
            )
            dynamo.put_item(
                TableName="Users",
                Item={"id": {"S": "1"}, "name": {"S": "Bob"}}
            )
            resp = dynamo.get_item(
                TableName="Users",
                Key={"id": {"S": "1"}}
            )
            self.assertEqual(resp["Item"]["name"]["S"], "Bob")

            # SQS
            sqs = kit.get_client("sqs")
            q = sqs.create_queue(QueueName="queue1")
            q_url = q["QueueUrl"]
            sqs.send_message(QueueUrl=q_url, MessageBody="msg1")
            msgs = sqs.receive_message(QueueUrl=q_url)
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

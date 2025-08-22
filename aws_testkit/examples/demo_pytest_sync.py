import pytest
from aws_testkit.src.moto_testkit import MotoTestKit

AWS_REGION = "us-east-1"

@pytest.fixture
def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=False)
    yield kit
    kit.close_clients()
    kit.stop()

def test_dynamodb(moto_kit):
    dynamo = moto_kit.get_client("dynamodb")
    dynamo.create_table(
        TableName="Users",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )
    dynamo.put_item(
        TableName="Users",
        Item={"id": {"S": "1"}, "name": {"S": "Alice"}}
    )
    resp = dynamo.get_item(
        TableName="Users",
        Key={"id": {"S": "1"}}
    )
    assert resp["Item"]["name"]["S"] == "Alice"

def test_sqs(moto_kit):
    sqs = moto_kit.get_client("sqs")
    q = sqs.create_queue(QueueName="queue1")
    q_url = q["QueueUrl"]
    sqs.send_message(QueueUrl=q_url, MessageBody="msg1")
    msgs = sqs.receive_message(QueueUrl=q_url)
    assert msgs["Messages"][0]["Body"] == "msg1"

def test_s3(moto_kit):
    s3 = moto_kit.get_client("s3")
    s3.create_bucket(Bucket="bucket1")
    s3.put_object(Bucket="bucket1", Key="file.txt", Body=b"abc")
    obj = s3.get_object(Bucket="bucket1", Key="file.txt")
    data = obj["Body"].read()
    assert data == b"abc"

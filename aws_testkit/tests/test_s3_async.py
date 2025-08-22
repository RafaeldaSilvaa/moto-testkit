# tests/test_s3_async.py
import pytest
from aws_testkit import S3ObjectModel

@pytest.mark.asyncio
async def test_s3_put_get_typed(moto_session):
    kit = moto_session
    # opcional: criar bucket via boto3 sync
    s3 = kit.get_client("s3")
    s3.create_bucket(Bucket="typed-bucket")

    s3_helper = kit.s3_helper()  # S3HelperTyped bound to the kit's ClientFactory
    payload = S3ObjectModel(bucket="typed-bucket", key="k.txt", body=b"hello world")

    # usa helper assincrono (aceita Pydantic model)
    await s3_helper.put_object_async(payload)
    body = await s3_helper.get_object_body_async("typed-bucket", "k.txt")
    assert body == b"hello world"

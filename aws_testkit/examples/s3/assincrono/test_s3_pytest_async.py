import pytest
import pytest_asyncio

from aws_testkit.src import MotoTestKit

@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    kit.close_clients()
    kit.stop()

@pytest.mark.asyncio
async def test_s3_put_and_list_objects(moto_kit):
    s3_client = moto_kit.get_client("s3")

    bucket_name = "meu-bucket"
    s3_client.create_bucket(Bucket=bucket_name)

    s3_client.put_object(
        Bucket=bucket_name,
        Key="arquivo.txt",
        Body=b"conteudo de teste"
    )

    resp = s3_client.list_objects_v2(Bucket=bucket_name)
    keys = [obj["Key"] for obj in resp.get("Contents", [])]

    assert "arquivo.txt" in keys

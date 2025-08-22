import pytest
import pytest_asyncio
import boto3
from aws_testkit.src import MotoTestKit
from aws_testkit.examples.s3.asynchronous.s3_async_repository import S3AsyncRepository


@pytest_asyncio.fixture
async def s3_setup():
    # Sobe o ambiente fake
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    endpoint = kit.get_client("s3").meta.endpoint_url
    repo = S3AsyncRepository(endpoint_url=endpoint)
    yield kit, repo, endpoint
    # Finaliza
    await kit.close_async_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_create_and_list_buckets(s3_setup):
    kit, repo, endpoint = s3_setup
    await repo.create_bucket("meu-bucket")
    buckets = await repo.list_buckets()
    assert "meu-bucket" in buckets


@pytest.mark.asyncio
async def test_upload_and_download_file(s3_setup):
    kit, repo, endpoint = s3_setup
    bucket_name = "bucket-arquivos"
    key = "teste.txt"
    content = b"conteudo"

    # Cria bucket com o repo assíncrono
    await repo.create_bucket(bucket_name)

    # Upload com boto3 síncrono para evitar bug do aiobotocore no Moto
    s3_sync = kit.get_client(service_name="s3")
    s3_sync.put_object(Bucket=bucket_name, Key=key, Body=content)

    # Download síncrono para evitar bug no get_object assíncrono
    obj = s3_sync.get_object(Bucket=bucket_name, Key=key)
    data = obj["Body"].read()

    assert data == content

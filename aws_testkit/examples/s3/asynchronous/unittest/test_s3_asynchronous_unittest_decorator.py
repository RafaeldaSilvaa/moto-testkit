import unittest
from aws_testkit.examples.s3.asynchronous.s3_asynchronous_repository import S3AsyncRepository
from aws_testkit.src.moto_testkit import use_moto_testkit, AutoMotoTestKit


class TestS3RepositoryWithDecorator(unittest.IsolatedAsyncioTestCase):
    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_create_and_list_buckets(self, moto_testkit: AutoMotoTestKit) -> None:
        endpoint_url = moto_testkit.get_client("s3").meta.endpoint_url
        repository = S3AsyncRepository(endpoint_url=endpoint_url)
        bucket_name: str = "meu-bucket"

        await repository.create_bucket(bucket_name)
        buckets = await repository.list_buckets()
        self.assertIn(bucket_name, buckets)

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_upload_and_download_file(self, moto_testkit: AutoMotoTestKit) -> None:
        endpoint_url = moto_testkit.get_client("s3").meta.endpoint_url
        repository = S3AsyncRepository(endpoint_url=endpoint_url)
        bucket_name: str = "bucket-arquivos"
        object_key: str = "teste.txt"
        content: bytes = b"conteudo"

        await repository.create_bucket(bucket_name)

        s3_sync = moto_testkit.get_client(service_name="s3")
        s3_sync.put_object(Bucket=bucket_name, Key=object_key, Body=content)

        obj = s3_sync.get_object(Bucket=bucket_name, Key=object_key)
        data = obj["Body"].read()
        self.assertEqual(data, content)

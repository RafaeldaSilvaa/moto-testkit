import unittest

from examples.s3.asynchronous.s3_asynchronous_repository import \
    S3AsyncRepository
from src import MotoTestKit


class TestS3RepositoryFixtureMotoTestKit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(
            auto_start=True, patch_aiobotocore=True
        )
        self.endpoint_url: str = self.moto_testkit.get_client("s3").meta.endpoint_url
        self.repository: S3AsyncRepository = S3AsyncRepository(
            endpoint_url=self.endpoint_url
        )

    async def asyncTearDown(self) -> None:
        await self.moto_testkit.close_async_clients()
        self.moto_testkit.stop()

    async def test_create_and_list_buckets(self) -> None:
        bucket_name: str = "meu-bucket"
        await self.repository.create_bucket(bucket_name)
        buckets = await self.repository.list_buckets()
        self.assertIn(bucket_name, buckets)

    async def test_upload_and_download_file(self) -> None:
        bucket_name: str = "bucket-arquivos"
        object_key: str = "teste.txt"
        content: bytes = b"conteudo"

        await self.repository.create_bucket(bucket_name)

        s3_sync = self.moto_testkit.get_client(service_name="s3")
        s3_sync.put_object(Bucket=bucket_name, Key=object_key, Body=content)

        obj = s3_sync.get_object(Bucket=bucket_name, Key=object_key)
        data = obj["Body"].read()
        self.assertEqual(data, content)

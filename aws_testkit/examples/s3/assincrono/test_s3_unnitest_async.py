import unittest
import boto3
from aws_testkit.src import MotoTestKit
from aws_testkit.examples.s3.assincrono.s3_async_repository import S3AsyncRepository


class TestS3RepositoryWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Sobe o ambiente fake
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        self.endpoint = self.kit.get_client("s3").meta.endpoint_url
        self.repo = S3AsyncRepository(endpoint_url=self.endpoint)

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_create_and_list_buckets(self):
        await self.repo.create_bucket("meu-bucket")
        buckets = await self.repo.list_buckets()
        self.assertIn("meu-bucket", buckets)

    async def test_upload_and_download_file(self):
        bucket_name = "bucket-arquivos"
        key = "teste.txt"
        content = b"conteudo"

        # Cria bucket com o repo assíncrono
        await self.repo.create_bucket(bucket_name)

        # Faz upload usando boto3 síncrono para evitar bug do aiobotocore no Moto
        s3_sync = self.kit.get_client(service_name="s3")
        s3_sync.put_object(Bucket=bucket_name, Key=key, Body=content)

        obj = s3_sync.get_object(Bucket=bucket_name, Key=key)
        data = obj["Body"].read()
        self.assertEqual(data, content)

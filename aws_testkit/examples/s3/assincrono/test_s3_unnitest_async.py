import unittest

from aws_testkit.src import MotoTestKit


class TestS3WithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    async def asyncTearDown(self):
        self.kit.close_clients()
        self.kit.stop()

    async def test_s3_create_and_list_buckets(self):
        s3_client = self.kit.get_client("s3")

        bucket_name = "meu-bucket"
        s3_client.create_bucket(Bucket=bucket_name)

        resp = s3_client.list_buckets()
        buckets = [b["Name"] for b in resp.get("Buckets", [])]

        self.assertIn(bucket_name, buckets)

    async def test_s3_upload_and_download(self):
        s3_client = self.kit.get_client("s3")

        bucket_name = "bucket-arquivos"
        s3_client.create_bucket(Bucket=bucket_name)

        s3_client.put_object(Bucket=bucket_name, Key="arquivo.txt", Body=b"conteudo")

        obj = s3_client.get_object(Bucket=bucket_name, Key="arquivo.txt")
        data = obj["Body"].read()

        self.assertEqual(data, b"conteudo")

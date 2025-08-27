import unittest

from aws_testkit.examples.s3.synchronous.s3_synchronous_repository import S3Repository
from aws_testkit.src import MotoTestKit


class TestS3RepositoryFixtureMotoTestKit(unittest.TestCase):
    def setUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(auto_start=True)
        self.repository: S3Repository = S3Repository(endpoint_url=self.moto_testkit.get_client("s3").meta.endpoint_url)

    def tearDown(self) -> None:
        self.moto_testkit.stop()

    def test_create_and_list_bucket(self) -> None:
        bucket_name: str = "my-bucket"
        self.repository.create_bucket(bucket_name)
        buckets = self.repository.list_buckets()
        self.assertIn(bucket_name, buckets)

    def test_upload_and_get_object(self) -> None:
        bucket_name: str = "my-bucket"
        key: str = "file.txt"
        content: bytes = b"hello"

        self.repository.create_bucket(bucket_name)
        self.repository.upload_object(bucket_name, key, content)
        data = self.repository.get_object(bucket_name, key)
        self.assertEqual(data, content)

    def test_delete_object(self) -> None:
        bucket_name: str = "my-bucket"
        key: str = "file.txt"
        content: bytes = b"bye"

        self.repository.create_bucket(bucket_name)
        self.repository.upload_object(bucket_name, key, content)
        self.repository.delete_object(bucket_name, key)

        with self.assertRaises(Exception):
            self.repository.get_object(bucket_name, key)

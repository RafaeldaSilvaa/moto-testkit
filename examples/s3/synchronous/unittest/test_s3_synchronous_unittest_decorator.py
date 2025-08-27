import unittest

from examples.s3.synchronous.s3_synchronous_repository import \
    S3Repository
from src.moto_testkit import AutoMotoTestKit, use_moto_testkit


class TestS3RepositoryWithDecorator(unittest.TestCase):
    @use_moto_testkit(auto_start=True)
    def test_create_and_list_bucket(self, moto_testkit: AutoMotoTestKit) -> None:
        repository = S3Repository(
            endpoint_url=moto_testkit.get_client("s3").meta.endpoint_url
        )
        bucket_name: str = "my-bucket"

        repository.create_bucket(bucket_name)
        buckets = repository.list_buckets()
        self.assertIn(bucket_name, buckets)

    @use_moto_testkit(auto_start=True)
    def test_upload_and_get_object(self, moto_testkit: AutoMotoTestKit) -> None:
        repository = S3Repository(
            endpoint_url=moto_testkit.get_client("s3").meta.endpoint_url
        )
        bucket_name: str = "my-bucket"
        key: str = "file.txt"
        content: bytes = b"hello"

        repository.create_bucket(bucket_name)
        repository.upload_object(bucket_name, key, content)
        data = repository.get_object(bucket_name, key)
        self.assertEqual(data, content)

    @use_moto_testkit(auto_start=True)
    def test_delete_object(self, moto_testkit: AutoMotoTestKit) -> None:
        repository = S3Repository(
            endpoint_url=moto_testkit.get_client("s3").meta.endpoint_url
        )
        bucket_name: str = "my-bucket"
        key: str = "file.txt"
        content: bytes = b"bye"

        repository.create_bucket(bucket_name)
        repository.upload_object(bucket_name, key, content)
        repository.delete_object(bucket_name, key)

        with self.assertRaises(Exception):
            repository.get_object(bucket_name, key)

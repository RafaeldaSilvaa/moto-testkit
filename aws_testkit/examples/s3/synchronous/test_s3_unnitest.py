import unittest
from aws_testkit.src import MotoTestKit
from s3_repository import S3Repository


class TestS3Repository(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True)
        self.repo = S3Repository(endpoint_url=self.kit.get_client("s3").meta.endpoint_url)

    def tearDown(self):
        self.kit.stop()

    def test_create_and_list_bucket(self):
        self.repo.create_bucket("my-bucket")
        buckets = self.repo.list_buckets()
        self.assertIn("my-bucket", buckets)

    def test_upload_and_get_object(self):
        self.repo.create_bucket("my-bucket")
        self.repo.upload_object("my-bucket", "file.txt", b"hello")
        data = self.repo.get_object("my-bucket", "file.txt")
        self.assertEqual(data, b"hello")

    def test_delete_object(self):
        self.repo.create_bucket("my-bucket")
        self.repo.upload_object("my-bucket", "file.txt", b"bye")
        self.repo.delete_object("my-bucket", "file.txt")
        with self.assertRaises(Exception):
            self.repo.get_object("my-bucket", "file.txt")

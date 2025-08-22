import pytest
from aws_testkit.src import MotoTestKit
from s3_repository import S3Repository


@pytest.fixture
def repo():
    kit = MotoTestKit(auto_start=True)
    repo = S3Repository(endpoint_url=kit.get_client("s3").meta.endpoint_url)
    yield repo
    kit.stop()


def test_create_and_list_bucket(repo):
    repo.create_bucket("my-bucket")
    assert "my-bucket" in repo.list_buckets()


def test_upload_and_get_object(repo):
    repo.create_bucket("my-bucket")
    repo.upload_object("my-bucket", "file.txt", b"hello")
    assert repo.get_object("my-bucket", "file.txt") == b"hello"


def test_delete_object(repo):
    repo.create_bucket("my-bucket")
    repo.upload_object("my-bucket", "file.txt", b"bye")
    repo.delete_object("my-bucket", "file.txt")
    with pytest.raises(Exception):
        repo.get_object("my-bucket", "file.txt")

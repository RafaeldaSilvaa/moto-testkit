import pytest

from aws_testkit.examples.s3.synchronous.s3_synchronous_repository import \
    S3Repository
from aws_testkit.src.moto_testkit import AutoMotoTestKit, use_moto_testkit


@use_moto_testkit(auto_start=True)
def test_create_and_list_bucket_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository = S3Repository(
        endpoint_url=moto_testkit.get_client("s3").meta.endpoint_url
    )
    bucket_name: str = "my-bucket"

    repository.create_bucket(bucket_name)
    assert bucket_name in repository.list_buckets()


@use_moto_testkit(auto_start=True)
def test_upload_and_get_object_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository = S3Repository(
        endpoint_url=moto_testkit.get_client("s3").meta.endpoint_url
    )
    bucket_name: str = "my-bucket"
    key: str = "file.txt"
    content: bytes = b"hello"

    repository.create_bucket(bucket_name)
    repository.upload_object(bucket_name, key, content)
    assert repository.get_object(bucket_name, key) == content


@use_moto_testkit(auto_start=True)
def test_delete_object_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository = S3Repository(
        endpoint_url=moto_testkit.get_client("s3").meta.endpoint_url
    )
    bucket_name: str = "my-bucket"
    key: str = "file.txt"
    content: bytes = b"bye"

    repository.create_bucket(bucket_name)
    repository.upload_object(bucket_name, key, content)
    repository.delete_object(bucket_name, key)

    with pytest.raises(Exception):
        repository.get_object(bucket_name, key)

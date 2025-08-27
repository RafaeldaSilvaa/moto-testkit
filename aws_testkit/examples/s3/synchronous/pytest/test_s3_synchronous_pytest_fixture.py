import pytest

from aws_testkit.examples.s3.synchronous.s3_synchronous_repository import \
    S3Repository
from aws_testkit.src import MotoTestKit


@pytest.fixture
def moto_testkit_fixture() -> S3Repository:
    """Inicializa MotoTestKit e retorna o repositório S3 síncrono configurado."""
    moto_testkit = MotoTestKit(auto_start=True)
    repository = S3Repository(
        endpoint_url=moto_testkit.get_client("s3").meta.endpoint_url
    )
    yield repository
    moto_testkit.stop()


def test_create_and_list_bucket_with_fixture(
    moto_testkit_fixture: S3Repository,
) -> None:
    bucket_name: str = "my-bucket"
    moto_testkit_fixture.create_bucket(bucket_name)
    assert bucket_name in moto_testkit_fixture.list_buckets()


def test_upload_and_get_object_with_fixture(moto_testkit_fixture: S3Repository) -> None:
    bucket_name: str = "my-bucket"
    key: str = "file.txt"
    content: bytes = b"hello"

    moto_testkit_fixture.create_bucket(bucket_name)
    moto_testkit_fixture.upload_object(bucket_name, key, content)
    assert moto_testkit_fixture.get_object(bucket_name, key) == content


def test_delete_object_with_fixture(moto_testkit_fixture: S3Repository) -> None:
    bucket_name: str = "my-bucket"
    key: str = "file.txt"
    content: bytes = b"bye"

    moto_testkit_fixture.create_bucket(bucket_name)
    moto_testkit_fixture.upload_object(bucket_name, key, content)
    moto_testkit_fixture.delete_object(bucket_name, key)

    with pytest.raises(Exception):
        moto_testkit_fixture.get_object(bucket_name, key)

import pytest
import pytest_asyncio

from examples.s3.asynchronous.s3_asynchronous_repository import S3AsyncRepository
from src import MotoTestKit


@pytest_asyncio.fixture
async def moto_testkit_fixture() -> tuple[MotoTestKit, S3AsyncRepository, str]:
    """Inicializa o MotoTestKit e o repositório S3 para testes assíncronos."""
    moto_testkit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    endpoint_url = moto_testkit.get_client("s3").meta.endpoint_url
    repository = S3AsyncRepository(endpoint_url=endpoint_url)
    yield moto_testkit, repository, endpoint_url
    await moto_testkit.close_async_clients()
    moto_testkit.stop()


@pytest.mark.asyncio
async def test_create_and_list_buckets_with_fixture(
    moto_testkit_fixture: tuple[MotoTestKit, S3AsyncRepository, str],
) -> None:
    _, repository, _ = moto_testkit_fixture
    bucket_name: str = "meu-bucket"

    await repository.create_bucket(bucket_name)
    buckets = await repository.list_buckets()

    assert bucket_name in buckets


@pytest.mark.asyncio
async def test_upload_and_download_file_with_fixture(
    moto_testkit_fixture: tuple[MotoTestKit, S3AsyncRepository, str],
) -> None:
    moto_testkit, repository, _ = moto_testkit_fixture
    bucket_name: str = "bucket-arquivos"
    object_key: str = "teste.txt"
    content: bytes = b"conteudo"

    await repository.create_bucket(bucket_name)

    s3_sync = moto_testkit.get_client(service_name="s3")
    s3_sync.put_object(Bucket=bucket_name, Key=object_key, Body=content)
    obj = s3_sync.get_object(Bucket=bucket_name, Key=object_key)
    data = obj["Body"].read()

    assert data == content

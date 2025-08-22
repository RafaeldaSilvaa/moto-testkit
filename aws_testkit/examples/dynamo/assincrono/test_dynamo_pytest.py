import pytest
import pytest_asyncio

from aws_testkit.src import MotoTestKit


@pytest_asyncio.fixture
async def moto_kit():
    kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
    yield kit
    await kit.close_async_clients()
    kit.stop()


@pytest.mark.asyncio
async def test_dynamodb_put_and_get_item(moto_kit):
    dynamo_client = await moto_kit.get_async_client("dynamodb")

    await dynamo_client.create_table(
        TableName="MinhaTabela",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST"
    )

    await dynamo_client.put_item(
        TableName="MinhaTabela",
        Item={"id": {"S": "123"}, "nome": {"S": "Teste"}}
    )

    resp = await dynamo_client.get_item(
        TableName="MinhaTabela",
        Key={"id": {"S": "123"}}
    )

    assert resp["Item"]["nome"]["S"] == "Teste"

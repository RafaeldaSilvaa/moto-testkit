from aws_testkit.src import DynamoItemModel


def test_dynamo_put_get(moto_session):
    kit = moto_session
    dynamo_helper = kit.dynamo_helper()  # DynamoHelperTyped
    dynamo_helper.create_table("users", key_name="id")

    item = DynamoItemModel(table="users", item={"id": {"S": "u1"}, "name": {"S": "Rafael"}})
    dynamo_helper.put_item(item)

    got = dynamo_helper.get_item("users", {"id": {"S": "u1"}})
    assert "Item" in got
    assert got["Item"]["name"]["S"] == "Rafael"

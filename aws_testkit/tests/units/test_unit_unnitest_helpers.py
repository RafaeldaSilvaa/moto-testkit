import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from aws_testkit.src.helpers import (DynamoHelperTyped, DynamoItemModel,
                                     S3HelperTyped, S3ObjectModel,
                                     SQSHelperTyped, SQSMessageModel)


class TestS3HelperTyped(unittest.TestCase):
    def setUp(self):
        self.mock_factory = MagicMock()
        self.helper = S3HelperTyped(self.mock_factory)

    def test_create_bucket(self):
        mock_client = MagicMock()
        self.mock_factory.get_client.return_value = mock_client
        mock_client.create_bucket.return_value = {"ok": True}

        result = self.helper.create_bucket("bucket1")

        self.mock_factory.get_client.assert_called_once_with("s3")
        mock_client.create_bucket.assert_called_once_with(Bucket="bucket1")
        self.assertEqual(result, {"ok": True})

    def test_put_object(self):
        model = S3ObjectModel(bucket="b1", key="k1", body=b"data")
        mock_client = MagicMock()
        self.mock_factory.get_client.return_value = mock_client
        mock_client.put_object.return_value = {"status": "uploaded"}

        result = self.helper.put_object(model)

        mock_client.put_object.assert_called_once_with(
            Bucket="b1", Key="k1", Body=b"data"
        )
        self.assertEqual(result, {"status": "uploaded"})

    def test_get_object_body(self):
        mock_body = MagicMock()
        mock_body.read.return_value = b"bytes"
        mock_client = MagicMock()
        mock_client.get_object.return_value = {"Body": mock_body}
        self.mock_factory.get_client.return_value = mock_client

        result = self.helper.get_object_body("b1", "k1")

        self.assertEqual(result, b"bytes")

    def test_put_object_async(self):
        model = S3ObjectModel(bucket="b1", key="k1", body=b"data")
        mock_client = AsyncMock()
        mock_client.put_object.return_value = {"async": True}
        self.mock_factory.get_async_client = AsyncMock(return_value=mock_client)

        result = asyncio.run(self.helper.put_object_async(model))

        mock_client.put_object.assert_awaited_once_with(
            Bucket="b1", Key="k1", Body=b"data"
        )
        self.assertEqual(result, {"async": True})

    def test_get_object_body_async(self):
        mock_body = AsyncMock()
        mock_body.read.return_value = b"abc"
        mock_client = AsyncMock()
        mock_client.get_object.return_value = {"Body": mock_body}
        self.mock_factory.get_async_client = AsyncMock(return_value=mock_client)

        result = asyncio.run(self.helper.get_object_body_async("b1", "k1"))

        self.assertEqual(result, b"abc")


class TestDynamoHelperTyped(unittest.TestCase):
    def setUp(self):
        self.mock_factory = MagicMock()
        self.helper = DynamoHelperTyped(self.mock_factory)

    def test_create_table(self):
        mock_client = MagicMock()
        mock_client.create_table.return_value = {"ok": 1}
        self.mock_factory.get_client.return_value = mock_client

        result = self.helper.create_table("tabela", key_name="id")

        self.mock_factory.get_client.assert_called_once_with("dynamodb")
        self.assertEqual(result, {"ok": 1})

    def test_put_item(self):
        model = DynamoItemModel(table="t1", item={"id": {"S": "1"}})
        mock_client = MagicMock()
        mock_client.put_item.return_value = {"ok": 2}
        self.mock_factory.get_client.return_value = mock_client

        result = self.helper.put_item(model)
        mock_client.put_item.assert_called_once_with(
            TableName="t1", Item={"id": {"S": "1"}}
        )
        self.assertEqual(result, {"ok": 2})

    def test_get_item(self):
        mock_client = MagicMock()
        mock_client.get_item.return_value = {"Item": {}}
        self.mock_factory.get_client.return_value = mock_client

        result = self.helper.get_item("t1", {"id": {"S": "1"}})

        mock_client.get_item.assert_called_once_with(
            TableName="t1", Key={"id": {"S": "1"}}
        )
        self.assertEqual(result, {"Item": {}})

    def test_put_item_async(self):
        model = DynamoItemModel(table="t1", item={"id": {"S": "1"}})
        mock_client = AsyncMock()
        mock_client.put_item.return_value = {"async": 3}
        self.mock_factory.get_async_client = AsyncMock(return_value=mock_client)

        result = asyncio.run(self.helper.put_item_async(model))
        self.assertEqual(result, {"async": 3})

    def test_get_item_async(self):
        mock_client = AsyncMock()
        mock_client.get_item.return_value = {"Item": {"id": {"S": "1"}}}
        self.mock_factory.get_async_client = AsyncMock(return_value=mock_client)

        result = asyncio.run(self.helper.get_item_async("t1", {"id": {"S": "1"}}))
        self.assertEqual(result, {"Item": {"id": {"S": "1"}}})


class TestSQSHelperTyped(unittest.TestCase):
    def setUp(self):
        self.mock_factory = MagicMock()
        self.helper = SQSHelperTyped(self.mock_factory)

    def test_create_queue(self):
        mock_client = MagicMock()
        mock_client.create_queue.return_value = {"QueueUrl": "url"}
        self.mock_factory.get_client.return_value = mock_client

        result = self.helper.create_queue("fila1")

        mock_client.create_queue.assert_called_once_with(QueueName="fila1")
        self.assertEqual(result, {"QueueUrl": "url"})

    def test_send_message(self):
        model = SQSMessageModel(queue_url="url", body="mensagem")
        mock_client = MagicMock()
        mock_client.send_message.return_value = {"ok": 4}
        self.mock_factory.get_client.return_value = mock_client

        result = self.helper.send_message(model)
        mock_client.send_message.assert_called_once_with(
            QueueUrl="url", MessageBody="mensagem"
        )
        self.assertEqual(result, {"ok": 4})

    def test_receive_messages(self):
        mock_client = MagicMock()
        mock_client.receive_message.return_value = {"Messages": []}
        self.mock_factory.get_client.return_value = mock_client

        result = self.helper.receive_messages("url", max_num=5)
        mock_client.receive_message.assert_called_once_with(
            QueueUrl="url", MaxNumberOfMessages=5
        )
        self.assertEqual(result, {"Messages": []})

    def test_send_message_async(self):
        model = SQSMessageModel(queue_url="url", body="msg")
        mock_client = AsyncMock()
        mock_client.send_message.return_value = {"async": 5}
        self.mock_factory.get_async_client = AsyncMock(return_value=mock_client)

        result = asyncio.run(self.helper.send_message_async(model))
        self.assertEqual(result, {"async": 5})

    def test_receive_messages_async(self):
        mock_client = AsyncMock()
        mock_client.receive_message.return_value = {"Messages": ["m1"]}
        self.mock_factory.get_async_client = AsyncMock(return_value=mock_client)

        result = asyncio.run(self.helper.receive_messages_async("url", max_num=2))
        self.assertEqual(result, {"Messages": ["m1"]})


if __name__ == "__main__":
    unittest.main()

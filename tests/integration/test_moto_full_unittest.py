import asyncio
import unittest

from src.helpers import (DynamoItemModel, S3ObjectModel,
                                     SQSMessageModel)
from src.moto_testkit import (AutoMotoTestKit, MotoTestKit,
                                          use_moto_testkit)


# =========================================================
# S3
# =========================================================
class TestS3Helper(unittest.TestCase):
    def test_s3_sync_with(self):
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=False) as kit:
            s3_helper = kit.s3_helper()
            bucket_name = "s3-synchronous-with"
            s3_helper.create_bucket(bucket_name)
            s3_helper.put_object(
                S3ObjectModel(bucket=bucket_name, key="f.txt", body=b"data")
            )
            self.assertEqual(s3_helper.get_object_body(bucket_name, "f.txt"), b"data")
            self.assertIn(
                bucket_name,
                [b["Name"] for b in kit.get_client("s3").list_buckets()["Buckets"]],
            )

    def test_s3_sync_without_with(self):
        kit = MotoTestKit(auto_start=True, patch_aiobotocore=False)
        s3_helper = kit.s3_helper()
        bucket_name = "s3-synchronous-bucket"
        file_key = "file.txt"
        file_content = b"abc"
        s3_helper.create_bucket(bucket_name)
        s3_helper.put_object(
            S3ObjectModel(bucket=bucket_name, key=file_key, body=file_content)
        )
        self.assertEqual(s3_helper.get_object_body(bucket_name, file_key), file_content)
        self.assertIn(
            bucket_name,
            [b["Name"] for b in kit.get_client("s3").list_buckets()["Buckets"]],
        )
        kit.close_clients()
        kit.stop()

    def test_s3_async_with(self):
        async def runner():
            async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
                # Usa helper/client S3 no modo síncrono
                s3_helper = kit.s3_helper()
                bucket_name = "s3-async-with-fallback"
                s3_helper.create_bucket(bucket_name)
                s3_helper.put_object(
                    S3ObjectModel(bucket=bucket_name, key="a.txt", body=b"xyz")
                )
                self.assertEqual(
                    s3_helper.get_object_body(bucket_name, "a.txt"), b"xyz"
                )
                buckets = kit.get_client("s3").list_buckets()["Buckets"]
                self.assertIn(bucket_name, [b["Name"] for b in buckets])

        asyncio.run(runner())

    def test_s3_async_without_with(self):
        async def runner():
            kit = AutoMotoTestKit(auto_start=True, patch_aiobotocore=True)
            kit.start()

            s3_helper = kit.s3_helper()
            bucket_name = "s3-async-no-with-fallback"
            s3_helper.create_bucket(bucket_name)
            s3_helper.put_object(
                S3ObjectModel(bucket=bucket_name, key="n.txt", body=b"123")
            )
            self.assertEqual(s3_helper.get_object_body(bucket_name, "n.txt"), b"123")
            buckets = kit.get_client("s3").list_buckets()["Buckets"]
            self.assertIn(bucket_name, [b["Name"] for b in buckets])

            kit.stop()

        asyncio.run(runner())

    @use_moto_testkit(auto_start=True, patch_aiobotocore=False)
    def test_s3_sync_decorator(self, moto_testkit):
        s3_helper = moto_testkit.s3_helper()
        bucket_name = "s3-sync-decorator"
        s3_helper.create_bucket(bucket_name)
        s3_helper.put_object(
            S3ObjectModel(bucket=bucket_name, key="f.txt", body=b"data")
        )
        self.assertEqual(s3_helper.get_object_body(bucket_name, "f.txt"), b"data")
        self.assertIn(
            bucket_name,
            [b["Name"] for b in moto_testkit.get_client("s3").list_buckets()["Buckets"]],
        )

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_s3_async_decorator(self, moto_testkit):
        s3_helper = moto_testkit.s3_helper()
        bucket_name = "s3-async-decorator"
        s3_helper.create_bucket(bucket_name)
        s3_helper.put_object(
            S3ObjectModel(bucket=bucket_name, key="a.txt", body=b"xyz")
        )
        self.assertEqual(s3_helper.get_object_body(bucket_name, "a.txt"), b"xyz")
        buckets = moto_testkit.get_client("s3").list_buckets()["Buckets"]
        self.assertIn(bucket_name, [b["Name"] for b in buckets])


# =========================================================
# DynamoDB
# =========================================================
class TestDynamoHelper(unittest.TestCase):
    def test_dynamo_sync_with(self):
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
            dynamo_helper = kit.dynamo_helper()
            table_name = "dynamo-synchronous-with"
            dynamo_helper.create_table(table_name, key_name="id")
            dynamo_helper.put_item(
                DynamoItemModel(table=table_name, item={"id": {"S": "1"}})
            )
            self.assertIn(
                table_name, kit.get_client("dynamodb").list_tables()["TableNames"]
            )

    def test_dynamo_sync_without_with(self):
        kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        dynamo_helper = kit.dynamo_helper()
        table_name = "users_table"
        dynamo_helper.create_table(table_name, key_name="id")
        dynamo_helper.put_item(
            DynamoItemModel(table=table_name, item={"id": {"S": "1"}})
        )
        self.assertIn(
            table_name, kit.get_client("dynamodb").list_tables()["TableNames"]
        )
        kit.close_clients()
        kit.stop()

    def test_dynamo_async_with(self):
        async def runner():
            async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
                dynamo_helper = kit.dynamo_helper()
                table_name = "products_table"
                dynamo_helper.create_table(table_name, key_name="sku")
                await dynamo_helper.put_item_async(
                    DynamoItemModel(table=table_name, item={"sku": {"S": "P1"}})
                )
                tables = (await (await kit.get_async_client("dynamodb")).list_tables())[
                    "TableNames"
                ]
                self.assertIn(table_name, tables)

        asyncio.run(runner())

    def test_dynamo_async_without_with(self):
        async def runner():
            kit = AutoMotoTestKit(auto_start=True, patch_aiobotocore=True)
            kit.start()
            dynamo_helper = kit.dynamo_helper()
            table_name = "dynamo-async-no-with"
            dynamo_helper.create_table(table_name, key_name="sku")
            await dynamo_helper.put_item_async(
                DynamoItemModel(table=table_name, item={"sku": {"S": "P2"}})
            )
            tables = (await (await kit.get_async_client("dynamodb")).list_tables())[
                "TableNames"
            ]
            self.assertIn(table_name, tables)
            kit.stop()

        asyncio.run(runner())

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    def test_dynamo_sync_decorator(self, moto_testkit):
        dynamo_helper = moto_testkit.dynamo_helper()
        table_name = "dynamo-sync-decorator"
        dynamo_helper.create_table(table_name, key_name="id")
        dynamo_helper.put_item(
            DynamoItemModel(table=table_name, item={"id": {"S": "1"}})
        )
        self.assertIn(
            table_name, moto_testkit.get_client("dynamodb").list_tables()["TableNames"]
        )

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_dynamo_async_decorator(self, moto):
        dynamo_helper = moto.dynamo_helper()
        table_name = "dynamo-async-decorator"
        dynamo_helper.create_table(table_name, key_name="sku")
        await dynamo_helper.put_item_async(
            DynamoItemModel(table=table_name, item={"sku": {"S": "P1"}})
        )
        tables = (await (await moto.get_async_client("dynamodb")).list_tables())[
            "TableNames"
        ]
        self.assertIn(table_name, tables)


# =========================================================
# SQS
# =========================================================
class TestSQSHelper(unittest.TestCase):
    def test_sqs_sync_with(self):
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
            sqs_helper = kit.sqs_helper()
            queue_name = "queue-synchronous-with"
            queue = sqs_helper.create_queue(queue_name)
            sqs_helper.send_message(
                SQSMessageModel(queue_url=queue["QueueUrl"], body="hello")
            )
            self.assertTrue(
                any(
                    queue_name in url
                    for url in kit.get_client("sqs").list_queues()["QueueUrls"]
                )
            )

    def test_sqs_sync_without_with(self):
        kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)
        sqs_helper = kit.sqs_helper()
        queue_name = "queue-synchronous"
        queue = sqs_helper.create_queue(queue_name)
        sqs_helper.send_message(
            SQSMessageModel(queue_url=queue["QueueUrl"], body="msg-synchronous")
        )
        self.assertTrue(
            any(
                queue_name in url
                for url in kit.get_client("sqs").list_queues()["QueueUrls"]
            )
        )
        kit.close_clients()
        kit.stop()

    def test_sqs_async_with(self):
        async def runner():
            async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
                sqs_helper = kit.sqs_helper()
                queue_name = "queue-async-with"
                queue = sqs_helper.create_queue(queue_name)
                await sqs_helper.send_message_async(
                    SQSMessageModel(queue_url=queue["QueueUrl"], body="msg")
                )
                queues = (await (await kit.get_async_client("sqs")).list_queues())[
                    "QueueUrls"
                ]
                self.assertTrue(any(queue_name in url for url in queues))

        asyncio.run(runner())

    def test_sqs_async_without_with(self):
        async def runner():
            kit = AutoMotoTestKit(auto_start=True, patch_aiobotocore=True)
            kit.start()
            sqs_helper = kit.sqs_helper()
            queue_name = "queue-async-no-with"
            queue = sqs_helper.create_queue(queue_name)
            await sqs_helper.send_message_async(
                SQSMessageModel(queue_url=queue["QueueUrl"], body="msg2")
            )
            queues = (await (await kit.get_async_client("sqs")).list_queues())[
                "QueueUrls"
            ]
            self.assertTrue(any(queue_name in url for url in queues))
            kit.stop()

        asyncio.run(runner())

    @use_moto_testkit(auto_start=True, patch_aiobotocore=False)
    def test_sqs_sync_decorator(self, moto_testkit):
        sqs_helper = moto_testkit.sqs_helper()
        queue_name = "queue-sync-decorator"
        queue = sqs_helper.create_queue(queue_name)
        sqs_helper.send_message(
            SQSMessageModel(queue_url=queue["QueueUrl"], body="hello")
        )
        self.assertTrue(
            any(
                queue_name in url
                for url in moto_testkit.get_client("sqs").list_queues()["QueueUrls"]
            )
        )

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_sqs_async_decorator(self, moto):
        sqs_helper = moto.sqs_helper()
        queue_name = "queue-async-decorator"
        queue = sqs_helper.create_queue(queue_name)
        await sqs_helper.send_message_async(
            SQSMessageModel(queue_url=queue["QueueUrl"], body="msg")
        )
        queues = (await (await moto.get_async_client("sqs")).list_queues())["QueueUrls"]
        self.assertTrue(any(queue_name in url for url in queues))


# =========================================================
# FULL
# =========================================================
class TestFullIntegration(unittest.TestCase):
    def test_full_sync_with(self):
        with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
            # S3
            s3_helper = kit.s3_helper()
            s3_helper.create_bucket("full-bucket-synchronous-with")
            s3_helper.put_object(
                S3ObjectModel(
                    bucket="full-bucket-synchronous-with", key="f.txt", body=b"abc"
                )
            )
            self.assertEqual(
                s3_helper.get_object_body("full-bucket-synchronous-with", "f.txt"),
                b"abc",
            )
            self.assertIn(
                "full-bucket-synchronous-with",
                [b["Name"] for b in kit.get_client("s3").list_buckets()["Buckets"]],
            )

            # Dynamo
            dynamo_helper = kit.dynamo_helper()
            dynamo_helper.create_table("full-users-with", key_name="id")
            dynamo_helper.put_item(
                DynamoItemModel(
                    table="full-users-with",
                    item={"id": {"S": "1"}, "name": {"S": "Bob"}},
                )
            )
            self.assertEqual(
                dynamo_helper.get_item("full-users-with", {"id": {"S": "1"}})["Item"][
                    "name"
                ]["S"],
                "Bob",
            )
            self.assertIn(
                "full-users-with",
                kit.get_client("dynamodb").list_tables()["TableNames"],
            )

            # SQS
            sqs_helper = kit.sqs_helper()
            queue = sqs_helper.create_queue("full-q-synchronous-with")
            sqs_helper.send_message(
                SQSMessageModel(queue_url=queue["QueueUrl"], body="msg-with")
            )
            msgs = sqs_helper.receive_messages(queue["QueueUrl"])
            self.assertEqual(msgs["Messages"][0]["Body"], "msg-with")
            self.assertTrue(
                any(
                    "full-q-synchronous-with" in url
                    for url in kit.get_client("sqs").list_queues()["QueueUrls"]
                )
            )

    def test_full_sync_without_with(self):
        kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

        # S3
        s3_helper = kit.s3_helper()
        s3_helper.create_bucket("full-bucket-synchronous")
        s3_helper.put_object(
            S3ObjectModel(bucket="full-bucket-synchronous", key="f.txt", body=b"abc")
        )
        self.assertEqual(
            s3_helper.get_object_body("full-bucket-synchronous", "f.txt"), b"abc"
        )
        self.assertIn(
            "full-bucket-synchronous",
            [b["Name"] for b in kit.get_client("s3").list_buckets()["Buckets"]],
        )

        # Dynamo
        dynamo_helper = kit.dynamo_helper()
        dynamo_helper.create_table("full-users", key_name="id")
        dynamo_helper.put_item(
            DynamoItemModel(
                table="full-users", item={"id": {"S": "1"}, "name": {"S": "Bob"}}
            )
        )
        self.assertEqual(
            dynamo_helper.get_item("full-users", {"id": {"S": "1"}})["Item"]["name"][
                "S"
            ],
            "Bob",
        )
        self.assertIn(
            "full-users", kit.get_client("dynamodb").list_tables()["TableNames"]
        )

        # SQS
        sqs_helper = kit.sqs_helper()
        queue = sqs_helper.create_queue("full-q-synchronous")
        sqs_helper.send_message(
            SQSMessageModel(queue_url=queue["QueueUrl"], body="full-synchronous-msg")
        )
        msgs = sqs_helper.receive_messages(queue["QueueUrl"])
        self.assertEqual(msgs["Messages"][0]["Body"], "full-synchronous-msg")
        self.assertTrue(
            any(
                "full-q-synchronous" in url
                for url in kit.get_client("sqs").list_queues()["QueueUrls"]
            )
        )

        kit.close_clients()
        kit.stop()

    def test_full_async_with(self):
        async def runner():
            async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
                # S3 (forçar síncrono para evitar bug moto + aiobotocore)
                s3_helper = kit.s3_helper()
                bucket_name = "full-bucket-async-with"
                file_key = "a.txt"
                file_content = b"xyz"

                s3_helper.create_bucket(bucket_name)
                s3_helper.put_object(
                    S3ObjectModel(bucket=bucket_name, key=file_key, body=file_content)
                )
                self.assertEqual(
                    s3_helper.get_object_body(bucket_name, file_key), file_content
                )

                buckets = kit.get_client("s3").list_buckets()["Buckets"]
                self.assertIn(bucket_name, [b["Name"] for b in buckets])

                # DynamoDB (async normalmente)
                dynamo_helper = kit.dynamo_helper()
                table_name = "full-prod-with"
                dynamo_helper.create_table(table_name, key_name="sku")
                await dynamo_helper.put_item_async(
                    DynamoItemModel(
                        table=table_name, item={"sku": {"S": "X"}, "price": {"N": "9"}}
                    )
                )
                self.assertEqual(
                    (
                        await dynamo_helper.get_item_async(
                            table_name, {"sku": {"S": "X"}}
                        )
                    )["Item"]["price"]["N"],
                    "9",
                )
                tables = (await (await kit.get_async_client("dynamodb")).list_tables())[
                    "TableNames"
                ]
                self.assertIn(table_name, tables)

                # SQS (async normalmente)
                sqs_helper = kit.sqs_helper()
                queue_name = "full-q-async-with"
                queue = sqs_helper.create_queue(queue_name)
                await sqs_helper.send_message_async(
                    SQSMessageModel(
                        queue_url=queue["QueueUrl"], body="full-async-msg-with"
                    )
                )
                msgs = await sqs_helper.receive_messages_async(queue["QueueUrl"])
                self.assertEqual(msgs["Messages"][0]["Body"], "full-async-msg-with")

                queues = (await (await kit.get_async_client("sqs")).list_queues())[
                    "QueueUrls"
                ]
                self.assertTrue(any(queue_name in url for url in queues))

        asyncio.run(runner())

    def test_full_async_without_with(self):
        async def runner():
            kit = AutoMotoTestKit(auto_start=True, patch_aiobotocore=True)
            kit.start()

            # S3 (modo síncrono para evitar bug do moto + aiobotocore)
            s3_helper = kit.s3_helper()
            bucket_name = "full-bucket-async-no-with"
            file_key = "n.txt"
            file_content = b"456"

            s3_helper.create_bucket(bucket_name)
            s3_helper.put_object(
                S3ObjectModel(bucket=bucket_name, key=file_key, body=file_content)
            )
            self.assertEqual(
                s3_helper.get_object_body(bucket_name, file_key), file_content
            )

            s3_client = kit.get_client("s3")
            buckets = s3_client.list_buckets()["Buckets"]
            self.assertIn(bucket_name, [b["Name"] for b in buckets])

            # DynamoDB (modo async normalmente)
            dynamo_helper = kit.dynamo_helper()
            table_name = "full-prod-no-with"
            dynamo_helper.create_table(table_name, key_name="sku")
            await dynamo_helper.put_item_async(
                DynamoItemModel(
                    table=table_name, item={"sku": {"S": "Y"}, "price": {"N": "5"}}
                )
            )
            self.assertEqual(
                (await dynamo_helper.get_item_async(table_name, {"sku": {"S": "Y"}}))[
                    "Item"
                ]["price"]["N"],
                "5",
            )
            tables = (await (await kit.get_async_client("dynamodb")).list_tables())[
                "TableNames"
            ]
            self.assertIn(table_name, tables)

            # SQS (modo async normalmente)
            sqs_helper = kit.sqs_helper()
            queue_name = "full-q-async-no-with"
            queue = sqs_helper.create_queue(queue_name)
            await sqs_helper.send_message_async(
                SQSMessageModel(
                    queue_url=queue["QueueUrl"], body="full-async-msg-no-with"
                )
            )
            msgs = await sqs_helper.receive_messages_async(queue["QueueUrl"])
            self.assertEqual(msgs["Messages"][0]["Body"], "full-async-msg-no-with")

            queues = (await (await kit.get_async_client("sqs")).list_queues())[
                "QueueUrls"
            ]
            self.assertTrue(any(queue_name in url for url in queues))

            kit.stop()

        asyncio.run(runner())

    @use_moto_testkit(auto_start=True, patch_aiobotocore=False)
    def test_full_sync_decorator(self, moto_testkit):
        # S3
        s3_helper = moto_testkit.s3_helper()
        s3_helper.create_bucket("full-bucket-sync-decorator")
        s3_helper.put_object(
            S3ObjectModel(bucket="full-bucket-sync-decorator", key="f.txt", body=b"abc")
        )
        self.assertEqual(
            s3_helper.get_object_body("full-bucket-sync-decorator", "f.txt"), b"abc"
        )
        self.assertIn(
            "full-bucket-sync-decorator",
            [b["Name"] for b in moto_testkit.get_client("s3").list_buckets()["Buckets"]],
        )

        # Dynamo
        dynamo_helper = moto_testkit.dynamo_helper()
        dynamo_helper.create_table("full-users-sync-decorator", key_name="id")
        dynamo_helper.put_item(
            DynamoItemModel(
                table="full-users-sync-decorator",
                item={"id": {"S": "1"}, "name": {"S": "Bob"}},
            )
        )
        self.assertEqual(
            dynamo_helper.get_item("full-users-sync-decorator", {"id": {"S": "1"}})[
                "Item"
            ]["name"]["S"],
            "Bob",
        )
        self.assertIn(
            "full-users-sync-decorator",
            moto_testkit.get_client("dynamodb").list_tables()["TableNames"],
        )

        # SQS
        sqs_helper = moto_testkit.sqs_helper()
        queue = sqs_helper.create_queue("full-q-sync-decorator")
        sqs_helper.send_message(
            SQSMessageModel(queue_url=queue["QueueUrl"], body="msg-with")
        )
        msgs = sqs_helper.receive_messages(queue["QueueUrl"])
        self.assertEqual(msgs["Messages"][0]["Body"], "msg-with")
        self.assertTrue(
            any(
                "full-q-sync-decorator" in url
                for url in moto_testkit.get_client("sqs").list_queues()["QueueUrls"]
            )
        )

    @use_moto_testkit(auto_start=True, patch_aiobotocore=True)
    async def test_full_async_decorator(self, moto):
        # S3 (sync helper para evitar bug moto + aiobotocore)
        s3_helper = moto.s3_helper()
        bucket_name = "full-bucket-async-decorator"
        file_key = "a.txt"
        file_content = b"xyz"

        s3_helper.create_bucket(bucket_name)
        s3_helper.put_object(
            S3ObjectModel(bucket=bucket_name, key=file_key, body=file_content)
        )
        self.assertEqual(s3_helper.get_object_body(bucket_name, file_key), file_content)

        buckets = moto.get_client("s3").list_buckets()["Buckets"]
        self.assertIn(bucket_name, [b["Name"] for b in buckets])

        # DynamoDB (modo async normalmente)
        dynamo_helper = moto.dynamo_helper()
        table_name = "full-prod-async-decorator"
        dynamo_helper.create_table(table_name, key_name="sku")
        await dynamo_helper.put_item_async(
            DynamoItemModel(
                table=table_name, item={"sku": {"S": "X"}, "price": {"N": "9"}}
            )
        )
        self.assertEqual(
            (await dynamo_helper.get_item_async(table_name, {"sku": {"S": "X"}}))[
                "Item"
            ]["price"]["N"],
            "9",
        )
        tables = (await (await moto.get_async_client("dynamodb")).list_tables())[
            "TableNames"
        ]
        self.assertIn(table_name, tables)

        # SQS (modo async normalmente)
        sqs_helper = moto.sqs_helper()
        queue_name = "full-q-async-decorator"
        queue = sqs_helper.create_queue(queue_name)
        await sqs_helper.send_message_async(
            SQSMessageModel(queue_url=queue["QueueUrl"], body="full-async-msg-with")
        )
        msgs = await sqs_helper.receive_messages_async(queue["QueueUrl"])
        self.assertEqual(msgs["Messages"][0]["Body"], "full-async-msg-with")

        queues = (await (await moto.get_async_client("sqs")).list_queues())["QueueUrls"]
        self.assertTrue(any(queue_name in url for url in queues))

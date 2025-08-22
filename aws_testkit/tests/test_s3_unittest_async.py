import unittest

from aws_testkit.src import MotoTestKit, S3ObjectModel


class AsyncS3TestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True)
        self.s3_helper = self.kit.s3_helper()
        # create bucket sync or await if using assincrono client
        self.kit.get_client("s3").create_bucket(Bucket="assincrono-bucket")

    async def asyncTearDown(self):
        await self.kit.close_clients()
        self.kit.stop()

    async def test_put_get_async(self):
        payload = S3ObjectModel(bucket="assincrono-bucket", key="a.txt", body=b"ok")
        await self.s3_helper.put_object_async(payload)
        body = await self.s3_helper.get_object_body_async("assincrono-bucket", "a.txt")
        self.assertEqual(body, b"ok")

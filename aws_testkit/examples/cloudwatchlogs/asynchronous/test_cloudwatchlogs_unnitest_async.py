import unittest

from aws_testkit.src import MotoTestKit


class TestCloudWatchLogsWithMoto(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kit = MotoTestKit(auto_start=True, patch_aiobotocore=True)

    async def asyncTearDown(self):
        await self.kit.close_async_clients()
        self.kit.stop()

    async def test_cloudwatchlogs_put_log_events(self):
        logs_client = await self.kit.get_async_client("logs")

        group_name = "meu-grupo-logs"
        stream_name = "meu-stream"

        await logs_client.create_log_group(logGroupName=group_name)
        await logs_client.create_log_stream(logGroupName=group_name, logStreamName=stream_name)

        put_resp = await logs_client.put_log_events(
            logGroupName=group_name,
            logStreamName=stream_name,
            logEvents=[
                {"timestamp": 1660000000000, "message": "Primeiro log"},
                {"timestamp": 1660000001000, "message": "Segundo log"}
            ]
        )

        self.assertIn("nextSequenceToken", put_resp)

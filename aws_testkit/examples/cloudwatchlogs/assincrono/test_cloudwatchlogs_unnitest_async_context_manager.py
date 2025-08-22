import unittest

from aws_testkit.src.moto_testkit import AutoMotoTestKit


class TestCloudWatchLogsWithMoto(unittest.IsolatedAsyncioTestCase):

    async def test_cloudwatchlogs_put_log_events(self):
        async with AutoMotoTestKit(auto_start=True, patch_aiobotocore=True) as kit:
            logs_client = await kit.get_async_client("logs")

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

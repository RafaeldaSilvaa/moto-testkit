import unittest
from aws_testkit.src import MotoTestKit
from cloudwatchlogs_repository import CloudWatchLogsRepository

class TestCloudWatchLogsRepository(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True)
        self.repo = CloudWatchLogsRepository(endpoint_url=self.kit.get_client("logs").meta.endpoint_url)

    def tearDown(self):
        self.kit.stop()

    def test_create_group_and_stream(self):
        self.repo.create_log_group("my-group")
        self.repo.create_log_stream("my-group", "my-stream")
        groups = self.repo.describe_log_groups()
        self.assertTrue(any(g["logGroupName"] == "my-group" for g in groups))

    def test_put_log_events(self):
        self.repo.create_log_group("my-group")
        self.repo.create_log_stream("my-group", "my-stream")
        resp = self.repo.put_log_events("my-group", "my-stream", ["msg1", "msg2"])
        self.assertIn("nextSequenceToken", resp)

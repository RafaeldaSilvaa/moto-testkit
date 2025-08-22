import boto3
from typing import Optional


class CloudWatchLogsRepository:
    def __init__(self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"):
        self.client = boto3.client("logs", endpoint_url=endpoint_url, region_name=region_name)

    def create_log_group(self, log_group_name: str):
        self.client.create_log_group(logGroupName=log_group_name)

    def create_log_stream(self, log_group_name: str, log_stream_name: str):
        self.client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)

    def put_log_events(self, log_group_name: str, log_stream_name: str, messages: list):
        events = [{"timestamp": 123456789, "message": m} for m in messages]
        return self.client.put_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            logEvents=events
        )

    def describe_log_groups(self):
        return self.client.describe_log_groups().get("logGroups", [])

from typing import List, Optional

import boto3


class S3Repository:
    def __init__(
        self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"
    ):
        self.client = boto3.client(
            "s3", endpoint_url=endpoint_url, region_name=region_name
        )

    def create_bucket(self, bucket_name: str):
        return self.client.create_bucket(Bucket=bucket_name)

    def list_buckets(self) -> List[str]:
        resp = self.client.list_buckets()
        return [b["Name"] for b in resp.get("Buckets", [])]

    def upload_object(self, bucket_name: str, key: str, data: bytes):
        self.client.put_object(Bucket=bucket_name, Key=key, Body=data)

    def get_object(self, bucket_name: str, key: str) -> bytes:
        resp = self.client.get_object(Bucket=bucket_name, Key=key)
        return resp["Body"].read()

    def delete_object(self, bucket_name: str, key: str):
        self.client.delete_object(Bucket=bucket_name, Key=key)

    def delete_bucket(self, bucket_name: str):
        self.client.delete_bucket(Bucket=bucket_name)

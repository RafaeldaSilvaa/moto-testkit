import aioboto3
from typing import Optional, List

class S3AsyncRepository:
    def __init__(self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"):
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.session = aioboto3.Session()

    async def create_bucket(self, bucket_name: str):
        async with self.session.client("s3", endpoint_url=self.endpoint_url, region_name=self.region_name) as client:
            return await client.create_bucket(Bucket=bucket_name)

    async def list_buckets(self) -> List[str]:
        async with self.session.client("s3", endpoint_url=self.endpoint_url, region_name=self.region_name) as client:
            resp = await client.list_buckets()
            return [b["Name"] for b in resp.get("Buckets", [])]

    async def upload_file(self, bucket_name: str, key: str, body: bytes):
        async with self.session.client("s3", endpoint_url=self.endpoint_url, region_name=self.region_name) as client:
            return await client.put_object(Bucket=bucket_name, Key=key, Body=body)

    async def download_file(self, bucket_name: str, key: str) -> bytes:
        async with self.session.client("s3", endpoint_url=self.endpoint_url, region_name=self.region_name) as client:
            resp = await client.get_object(Bucket=bucket_name, Key=key)
            return await resp["Body"].read()

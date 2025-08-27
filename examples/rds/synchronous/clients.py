import boto3

from .config import settings


class AwsClients:
    def __init__(
        self, region_name: str | None = None, rds_endpoint_url: str | None = None
    ):
        self._region = region_name or settings.aws_region
        self._rds_endpoint = rds_endpoint_url or settings.rds_endpoint_url
        self._rds_client = None

    def rds(self):
        if self._rds_client is None:
            self._rds_client = boto3.client(
                "rds", region_name=self._region, endpoint_url=self._rds_endpoint
            )
        return self._rds_client

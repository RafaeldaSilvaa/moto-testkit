import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    aws_region: str = os.getenv("AWS_REGION", "eu-central-1")
    rds_endpoint_url: str | None = os.getenv("ENDPOINT_URL_RDS")


settings = Settings()

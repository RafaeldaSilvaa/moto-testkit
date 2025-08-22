# moto-testkit — docs

Use the session fixture in pytest (no start/stop needed).

Example:
```py
from aws_testkit import S3ObjectModel

def test_x(moto_session):
    s3 = moto_session.get_client("s3")
    s3.create_bucket(Bucket="b")

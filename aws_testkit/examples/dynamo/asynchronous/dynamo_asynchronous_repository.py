import aioboto3
from typing import Optional, List, Dict


class DynamoDBAsyncRepository:
    def __init__(self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"):
        self.endpoint_url = endpoint_url
        self.region_name = region_name

    async def create_table(
        self, table_name: str, key_schema: List[Dict], attribute_definitions: List[Dict], provisioned_throughput: Dict
    ):
        async with aioboto3.Session().client(
            "dynamodb", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            return await client.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput=provisioned_throughput,
            )

    async def put_item(self, table_name: str, item: Dict):
        async with aioboto3.Session().client(
            "dynamodb", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            await client.put_item(TableName=table_name, Item=item)

    async def get_item(self, table_name: str, key: Dict):
        async with aioboto3.Session().client(
            "dynamodb", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            resp = await client.get_item(TableName=table_name, Key=key)
            return resp.get("Item")

    async def query_items(self, table_name: str, key_condition_expression, expression_attribute_values: Dict):
        async with aioboto3.Session().client(
            "dynamodb", endpoint_url=self.endpoint_url, region_name=self.region_name
        ) as client:
            resp = await client.query(
                TableName=table_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
            )
            return resp.get("Items", [])

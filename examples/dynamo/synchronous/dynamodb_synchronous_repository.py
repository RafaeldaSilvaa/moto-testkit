# dynamodb_synchronous_repository.py
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError


class DynamoDBRepository:
    def __init__(
        self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"
    ):
        self.client = boto3.client(
            "dynamodb", endpoint_url=endpoint_url, region_name=region_name
        )

    def create_table(
        self,
        table_name: str,
        key_schema: List[Dict],
        attribute_definitions: List[Dict],
        provisioned_throughput: Dict,
    ):
        return self.client.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput,
        )

    def put_item(self, table_name: str, item: Dict):
        self.client.put_item(TableName=table_name, Item=item)

    def get_item(self, table_name: str, key: Dict) -> Optional[Dict]:
        resp = self.client.get_item(TableName=table_name, Key=key)
        return resp.get("Item")

    def delete_item(self, table_name: str, key: Dict):
        self.client.delete_item(TableName=table_name, Key=key)

    def list_tables(self) -> List[str]:
        return self.client.list_tables().get("TableNames", [])

    def query_items(
        self,
        table_name: str,
        key_condition_expression,
        expression_attribute_values: Dict,
    ):
        """
        key_condition_expression: Ex: 'id = :id'
        expression_attribute_values: Ex: {':id': {'S': '123'}}
        """
        resp = self.client.query(
            TableName=table_name,
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values,
        )
        return resp.get("Items", [])

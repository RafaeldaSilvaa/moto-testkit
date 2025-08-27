from typing import Optional

import boto3


class StepFunctionsRepository:
    def __init__(
        self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"
    ):
        self.client = boto3.client(
            "stepfunctions", endpoint_url=endpoint_url, region_name=region_name
        )

    def create_state_machine(self, name: str, definition: str, role_arn: str):
        return self.client.create_state_machine(
            name=name, definition=definition, roleArn=role_arn
        )

    def start_execution(self, state_machine_arn: str, input_data: str):
        return self.client.start_execution(
            stateMachineArn=state_machine_arn, input=input_data
        )

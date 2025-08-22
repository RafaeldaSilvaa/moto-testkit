import aioboto3
from typing import Optional


class StepFunctionsAsyncRepository:
    def __init__(self, endpoint_url: Optional[str] = None, region_name: str = "us-east-1"):
        self.endpoint_url = endpoint_url
        self.region_name = region_name

    async def create_state_machine(self, name: str, definition: str, role_arn: str):
        async with aioboto3.Session().client("stepfunctions", endpoint_url=self.endpoint_url, region_name=self.region_name) as client:
            return await client.create_state_machine(
                name=name,
                definition=definition,
                roleArn=role_arn
            )

    async def start_execution(self, state_machine_arn: str, input_data: str):
        async with aioboto3.Session().client("stepfunctions", endpoint_url=self.endpoint_url, region_name=self.region_name) as client:
            return await client.start_execution(
                stateMachineArn=state_machine_arn,
                input=input_data
            )

"""
DynamoDB service wrapper for FarmMate NZ.

Local dev: points at DynamoDB Local (via Docker Compose) using dummy credentials.
Deployed:  points at real AWS DynamoDB, using the EC2 instance's IAM role
           (no credentials needed in code — boto3 picks them up automatically).

Toggle is controlled by the DYNAMODB_ENDPOINT_URL env var:
  - set to "http://dynamodb-local:8000" for local Docker Compose dev
  - unset / not present in production, so boto3 talks to real AWS
"""

import os
import boto3

AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")  # Sydney, closest AWS region to NZ
# Container-to-container URL (used when the FastAPI app itself runs inside Docker Compose).
# For scripts run on the host machine (e.g. db/init_dynamodb.py), use http://localhost:8001 instead.
DYNAMODB_ENDPOINT_URL = os.getenv("DYNAMODB_ENDPOINT_URL")

def get_dynamo_resource():
    """
    Returns a boto3 DynamoDB resource, pointed at either DynamoDB Local
    (if DYNAMODB_ENDPOINT_URL is set) or real AWS (if not set).
    """
    if DYNAMODB_ENDPOINT_URL:
        # Local dev: DynamoDB Local doesn't check credentials, but boto3
        # requires *something* to be present, so we pass dummy values.
        return boto3.resource(
            "dynamodb",
            endpoint_url=DYNAMODB_ENDPOINT_URL,
            region_name=AWS_REGION,
            aws_access_key_id="local",
            aws_secret_access_key="local",
        )
    else:
        # Production: boto3 automatically uses the EC2 instance's IAM role.
        return boto3.resource("dynamodb", region_name=AWS_REGION)


# Table name constants — keep in one place so routes don't hardcode strings
TABLE_FARMS = "Farms"
TABLE_PADDOCKS = "Paddocks"
TABLE_LIVESTOCK = "Livestock"
TABLE_TASK_LOGS = "TaskLogs"
TABLE_ALERT_STATE = "AlertState"
TABLE_USERS = "Users"


def get_table(table_name: str):
    """Convenience helper: get a specific table resource."""
    dynamodb = get_dynamo_resource()
    return dynamodb.Table(table_name)

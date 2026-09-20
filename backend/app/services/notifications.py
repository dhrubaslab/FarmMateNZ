"""
SNS notification service — sends alert emails via a subscribed SNS topic.
"""

import os
import boto3

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

_sns_client = boto3.client("sns", region_name=AWS_REGION)


def send_alert_notification(farm_id: str, alert_type: str, message: str):
    """Publishes an alert to the SNS topic. No-ops if SNS_TOPIC_ARN isn't set."""
    if not SNS_TOPIC_ARN:
        print(f"SNS_TOPIC_ARN not configured — skipping notification for {farm_id}/{alert_type}")
        return

    _sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"FarmMate NZ Alert: {alert_type.replace('_', ' ').title()}",
        Message=f"Farm {farm_id}: {message}",
    )
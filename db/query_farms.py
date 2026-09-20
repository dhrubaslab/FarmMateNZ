import boto3

table = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8001",
    region_name="us-east-1",
    aws_access_key_id="local",
    aws_secret_access_key="local",
).Table("Farms")

for item in table.scan()["Items"]:
    print(item)

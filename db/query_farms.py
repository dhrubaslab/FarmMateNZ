import boto3

table = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    region_name="ap-southeast-2",
    aws_access_key_id="local",
    aws_secret_access_key="local",
).Table("Farms")

for item in table.scan()["Items"]:
    print(item)

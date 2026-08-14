"""Create DynamoDB tables and load simulation data against DynamoDB Local.

Placeholder schema: extend TABLES / SIMULATION_DATA once the real data
model is decided.
"""
import boto3

ENDPOINT_URL = "http://localhost:8000"
REGION = "ap-southeast-2"

TABLES = [
    {
        "TableName": "Farms",
        "KeySchema": [{"AttributeName": "farm_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "farm_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    }
]

SIMULATION_DATA = {
    "Farms": [
        {"farm_id": "farm-001", "name": "Sunnyside Dairy", "region": "Waikato", "size_hectares": 120},
        {"farm_id": "farm-002", "name": "Green Valley Farm", "region": "Canterbury", "size_hectares": 85},
        {"farm_id": "farm-003", "name": "Coastal Pastures", "region": "Bay of Plenty", "size_hectares": 60},
    ]
}


def _client():
    return boto3.client(
        "dynamodb",
        endpoint_url=ENDPOINT_URL,
        region_name=REGION,
        aws_access_key_id="local",
        aws_secret_access_key="local",
    )


def _resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=ENDPOINT_URL,
        region_name=REGION,
        aws_access_key_id="local",
        aws_secret_access_key="local",
    )


def create_tables(client):
    existing = client.list_tables()["TableNames"]
    for table in TABLES:
        if table["TableName"] in existing:
            print(f"Table '{table['TableName']}' already exists, skipping creation.")
            continue
        client.create_table(**table)
        client.get_waiter("table_exists").wait(TableName=table["TableName"])
        print(f"Created table '{table['TableName']}'.")


def seed_data(resource):
    for table_name, items in SIMULATION_DATA.items():
        table = resource.Table(table_name)
        for item in items:
            table.put_item(Item=item)
        print(f"Seeded {len(items)} item(s) into '{table_name}'.")


def main():
    create_tables(_client())
    seed_data(_resource())


if __name__ == "__main__":
    main()

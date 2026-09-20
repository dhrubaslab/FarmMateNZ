"""Create DynamoDB tables and load simulation data against DynamoDB Local.

Placeholder schema: extend TABLES / SIMULATION_DATA further once the real
data model is finalised.
"""
from decimal import Decimal

import boto3

ENDPOINT_URL = "http://localhost:8001"
REGION = "us-east-1"

TABLES = [
    {
        "TableName": "Farms",
        "KeySchema": [{"AttributeName": "farm_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "farm_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "Paddocks",
        "KeySchema": [
            {"AttributeName": "farm_id", "KeyType": "HASH"},
            {"AttributeName": "paddock_id", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "farm_id", "AttributeType": "S"},
            {"AttributeName": "paddock_id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "Livestock",
        "KeySchema": [
            {"AttributeName": "farm_id", "KeyType": "HASH"},
            {"AttributeName": "livestock_id", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "farm_id", "AttributeType": "S"},
            {"AttributeName": "livestock_id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "TaskLogs",
        "KeySchema": [
            {"AttributeName": "farm_id", "KeyType": "HASH"},
            # e.g. "2026-08-16T10:00:00#task-001" — keeps logs naturally time-ordered
            {"AttributeName": "timestamp_task_id", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "farm_id", "AttributeType": "S"},
            {"AttributeName": "timestamp_task_id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "AlertState",
        "KeySchema": [
            {"AttributeName": "farm_id", "KeyType": "HASH"},
            # e.g. "frost", "heavy_rain", "low_soil_moisture"
            {"AttributeName": "alert_type", "KeyType": "RANGE"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "farm_id", "AttributeType": "S"},
            {"AttributeName": "alert_type", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "Users",
        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "user_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        # Populated by the backend's weather sync (services/weather.py), not seeded here.
        "TableName": "WeatherData",
        "KeySchema": [{"AttributeName": "farm_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "farm_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
]

SIMULATION_DATA = {
    "Farms": [
        {"farm_id": "farm-001", "name": "Sunnyside Dairy", "region": "Waikato", "size_hectares": 120,
         "latitude": Decimal("-37.78"), "longitude": Decimal("175.28")},
        {"farm_id": "farm-002", "name": "Green Valley Farm", "region": "Canterbury", "size_hectares": 85,
         "latitude": Decimal("-43.53"), "longitude": Decimal("172.63")},
        {"farm_id": "farm-003", "name": "Coastal Pastures", "region": "Bay of Plenty", "size_hectares": 60,
         "latitude": Decimal("-37.69"), "longitude": Decimal("176.17")},
        {"farm_id": "farm-004", "name": "Kaitaia Farm", "region": "Kaitaia", "size_hectares": 50,
         "latitude": Decimal("-35.1141"), "longitude": Decimal("173.2637")},
        {"farm_id": "farm-005", "name": "Whangarei Farm", "region": "Whangarei", "size_hectares": 50,
         "latitude": Decimal("-35.7275"), "longitude": Decimal("174.3166")},
        {"farm_id": "farm-006", "name": "Auckland Farm", "region": "Auckland", "size_hectares": 50,
         "latitude": Decimal("-36.8485"), "longitude": Decimal("174.7633")},
        {"farm_id": "farm-007", "name": "Hamilton Farm", "region": "Hamilton", "size_hectares": 50,
         "latitude": Decimal("-37.7870"), "longitude": Decimal("175.2793")},
        {"farm_id": "farm-008", "name": "Tauranga Farm", "region": "Tauranga", "size_hectares": 50,
         "latitude": Decimal("-37.6878"), "longitude": Decimal("176.1651")},
        {"farm_id": "farm-009", "name": "Rotorua Farm", "region": "Rotorua", "size_hectares": 50,
         "latitude": Decimal("-38.1368"), "longitude": Decimal("176.2497")},
        {"farm_id": "farm-010", "name": "Gisborne Farm", "region": "Gisborne", "size_hectares": 50,
         "latitude": Decimal("-38.6623"), "longitude": Decimal("178.0176")},
        {"farm_id": "farm-011", "name": "New Plymouth Farm", "region": "New Plymouth", "size_hectares": 50,
         "latitude": Decimal("-39.0556"), "longitude": Decimal("174.0752")},
        {"farm_id": "farm-012", "name": "Napier Farm", "region": "Napier", "size_hectares": 50,
         "latitude": Decimal("-39.4928"), "longitude": Decimal("176.9120")},
        {"farm_id": "farm-013", "name": "Palmerston North Farm", "region": "Palmerston North", "size_hectares": 50,
         "latitude": Decimal("-40.3523"), "longitude": Decimal("175.6082")},
        {"farm_id": "farm-014", "name": "Wellington Farm", "region": "Wellington", "size_hectares": 50,
         "latitude": Decimal("-41.2865"), "longitude": Decimal("174.7762")},
        {"farm_id": "farm-015", "name": "Nelson Farm", "region": "Nelson", "size_hectares": 50,
         "latitude": Decimal("-41.2706"), "longitude": Decimal("173.2840")},
        {"farm_id": "farm-016", "name": "Blenheim Farm", "region": "Blenheim", "size_hectares": 50,
         "latitude": Decimal("-41.5134"), "longitude": Decimal("173.9612")},
        {"farm_id": "farm-017", "name": "Westport Farm", "region": "Westport", "size_hectares": 50,
         "latitude": Decimal("-41.7545"), "longitude": Decimal("171.6039")},
        {"farm_id": "farm-018", "name": "Greymouth Farm", "region": "Greymouth", "size_hectares": 50,
         "latitude": Decimal("-42.4500"), "longitude": Decimal("171.2100")},
        {"farm_id": "farm-019", "name": "Christchurch Farm", "region": "Christchurch", "size_hectares": 50,
         "latitude": Decimal("-43.5321"), "longitude": Decimal("172.6362")},
        {"farm_id": "farm-020", "name": "Timaru Farm", "region": "Timaru", "size_hectares": 50,
         "latitude": Decimal("-44.3904"), "longitude": Decimal("171.2373")},
        {"farm_id": "farm-021", "name": "Queenstown Farm", "region": "Queenstown", "size_hectares": 50,
         "latitude": Decimal("-45.0312"), "longitude": Decimal("168.6626")},
        {"farm_id": "farm-022", "name": "Dunedin Farm", "region": "Dunedin", "size_hectares": 50,
         "latitude": Decimal("-45.8788"), "longitude": Decimal("170.5028")},
        {"farm_id": "farm-023", "name": "Invercargill Farm", "region": "Invercargill", "size_hectares": 50,
         "latitude": Decimal("-46.4132"), "longitude": Decimal("168.3538")},
        {"farm_id": "farm-024", "name": "Oban Farm", "region": "Oban (Stewart Island)", "size_hectares": 50,
         "latitude": Decimal("-46.8975"), "longitude": Decimal("168.1298")},
    ],
    "Paddocks": [
        {"farm_id": "farm-001", "paddock_id": "paddock-01", "name": "North Block", "area_hectares": 15, "stock_type": "dairy"},
        {"farm_id": "farm-001", "paddock_id": "paddock-02", "name": "River Flat", "area_hectares": 10, "stock_type": "dairy"},
        {"farm_id": "farm-002", "paddock_id": "paddock-01", "name": "Home Paddock", "area_hectares": 20, "stock_type": "beef"},
    ],
    "Livestock": [
        {"farm_id": "farm-001", "livestock_id": "stock-01", "type": "dairy cow", "count": 85, "paddock_id": "paddock-01"},
        {"farm_id": "farm-002", "livestock_id": "stock-01", "type": "beef cattle", "count": 40, "paddock_id": "paddock-01"},
        {"farm_id": "farm-003", "livestock_id": "stock-01", "type": "sheep", "count": 200, "paddock_id": "paddock-01"},
    ],
    "TaskLogs": [
        {"farm_id": "farm-001", "timestamp_task_id": "2026-08-01T08:00:00#task-001", "task": "Drenching", "paddock_id": "paddock-01"},
        {"farm_id": "farm-001", "timestamp_task_id": "2026-08-05T09:30:00#task-002", "task": "Moved stock", "paddock_id": "paddock-02"},
        {"farm_id": "farm-002", "timestamp_task_id": "2026-08-03T07:00:00#task-001", "task": "Mowing", "paddock_id": "paddock-01"},
    ],
    "AlertState": [
        {"farm_id": "farm-001", "alert_type": "frost", "last_triggered": None, "threshold_celsius": 2},
        {"farm_id": "farm-001", "alert_type": "heavy_rain", "last_triggered": None, "threshold_mm": 50},
        {"farm_id": "farm-002", "alert_type": "low_soil_moisture", "last_triggered": None, "threshold_percent": 20},
    ],
"Users": [
    {
        "user_id": "user-001",
        "email": "superadmin@farmmate.nz",
        "name": "Super Admin",
        "hashed_password": "$2b$12$LHwIuelO4wSkFC1ajn2/HuIZSdqTJT9D0HrQYv5TQQEQQvOj1yrrq",
        "role": "super-admin",
        "farm_id": None,
        "status": "active",
    },
    {
        "user_id": "user-002",
        "email": "admin@sunnyside.nz",
        "name": "Sunnyside Admin",
        "hashed_password": "$2b$12$LHwIuelO4wSkFC1ajn2/HuIZSdqTJT9D0HrQYv5TQQEQQvOj1yrrq",
        "role": "admin",
        "farm_id": "farm-001",
        "status": "active",
    },
    {
        "user_id": "user-003",
        "email": "staff@sunnyside.nz",
        "name": "Sunnyside Staff",
        "hashed_password": "$2b$12$LHwIuelO4wSkFC1ajn2/HuIZSdqTJT9D0HrQYv5TQQEQQvOj1yrrq",
        "role": "staff",
        "farm_id": "farm-001",
        "status": "active",
    },
],
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

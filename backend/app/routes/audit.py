from boto3.dynamodb.conditions import Attr, Key
from fastapi import APIRouter, Depends, Query

from app.services.dynamo import get_table, TABLE_AUDIT_LOGS
from app.services.permissions import Role, require_roles

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("")
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN)),
):
    query = {
        "KeyConditionExpression": Key("log_type").eq("audit"),
        "ScanIndexForward": False,  # newest first
    }
    if current_user["role"] == Role.SUPER_ADMIN.value:
        query["Limit"] = limit
    elif current_user.get("farm_id"):
        query["FilterExpression"] = Attr("actor_farm_id").eq(current_user["farm_id"])
    else:
        return []

    table = get_table(TABLE_AUDIT_LOGS)
    items = []
    while len(items) < limit:
        response = table.query(**query)
        items += response.get("Items", [])
        if "LastEvaluatedKey" not in response:
            break
        query["ExclusiveStartKey"] = response["LastEvaluatedKey"]
    return [_readable(item) for item in items[:limit]]


def _readable(item: dict) -> dict:
    """Time and message first; drop the storage-only keys."""
    lead = {"timestamp": item["timestamp"], "message": item.get("message") or f"{item['method']} {item['path']}"}
    rest = {k: v for k, v in item.items() if k not in ("log_type", "timestamp_id", *lead)}
    return {**lead, **rest}

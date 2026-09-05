"""
Shared AlertState logic, used by both the alerts API routes
and the weather sync background job.
"""

from datetime import datetime, timezone
from app.services.dynamo import get_table, TABLE_ALERT_STATE

ALERT_TYPES = ("frost", "heavy_rain", "low_soil_moisture")


def set_alert_state(farm_id: str, alert_type: str, active: bool, message: str | None = None):
    table = get_table(TABLE_ALERT_STATE)
    now = datetime.now(timezone.utc).isoformat()

    item = {
        "farm_id": farm_id,
        "alert_type": alert_type,
        "active": active,
        "message": message,
        "updated_at": now,
    }
    if active:
        item["triggered_at"] = now
        item["acknowledged"] = False
        item["acknowledged_by"] = None
        item["acknowledged_at"] = None

    table.update_item(
        Key={"farm_id": farm_id, "alert_type": alert_type},
        UpdateExpression=(
            "SET active = :a, message = :m, updated_at = :u"
            + (", triggered_at = :t, acknowledged = :ack, acknowledged_by = :ab, acknowledged_at = :aa" if active else "")
        ),
        ExpressionAttributeValues=(
            {":a": active, ":m": message, ":u": now, ":t": now, ":ack": False, ":ab": None, ":aa": None}
            if active
            else {":a": active, ":m": message, ":u": now}
        ),
    )
    return item
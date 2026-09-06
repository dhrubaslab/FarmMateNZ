from datetime import datetime, timezone
from app.services.dynamo import get_table, TABLE_ALERT_STATE
from app.services.notifications import send_alert_notification

ALERT_TYPES = ("frost", "heavy_rain", "low_soil_moisture")


def set_alert_state(farm_id: str, alert_type: str, active: bool, message: str | None = None):
    table = get_table(TABLE_ALERT_STATE)
    now = datetime.now(timezone.utc).isoformat()

    existing = table.get_item(Key={"farm_id": farm_id, "alert_type": alert_type}).get("Item")
    was_active = existing.get("active", False) if existing else False

    if active:
        table.update_item(
            Key={"farm_id": farm_id, "alert_type": alert_type},
            UpdateExpression=(
                "SET active = :a, message = :m, updated_at = :u, "
                "triggered_at = :t, acknowledged = :ack, acknowledged_by = :ab, acknowledged_at = :aa"
            ),
            ExpressionAttributeValues={
                ":a": True, ":m": message, ":u": now,
                ":t": now, ":ack": False, ":ab": None, ":aa": None,
            },
        )
        if not was_active:
            send_alert_notification(farm_id, alert_type, message or "Threshold exceeded")
    else:
        table.update_item(
            Key={"farm_id": farm_id, "alert_type": alert_type},
            UpdateExpression="SET active = :a, message = :m, updated_at = :u",
            ExpressionAttributeValues={":a": False, ":m": message, ":u": now},
        )

    return table.get_item(Key={"farm_id": farm_id, "alert_type": alert_type})["Item"]
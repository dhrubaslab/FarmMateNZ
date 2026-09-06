"""
AlertState routes.

Access rules (from services/permissions.py):
- super-admin: view/acknowledge/manually set any farm's alerts
- admin: view/acknowledge/manually set alerts for their OWN farm only
- staff: view alerts for their OWN farm only (read-only)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone
from app.services.dynamo import get_table, TABLE_ALERT_STATE
from app.services.permissions import Role, require_same_farm_or_super_admin
from app.services.alerts import set_alert_state, ALERT_TYPES

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertState(BaseModel):
    farm_id: str
    alert_type: str
    active: bool
    message: str | None = None
    triggered_at: str | None = None
    updated_at: str | None = None
    acknowledged: bool = False
    acknowledged_by: str | None = None
    acknowledged_at: str | None = None


class AlertUpdate(BaseModel):
    active: bool
    message: str | None = None


@router.get("/{farm_id}", response_model=list[AlertState])
def list_alerts(farm_id: str, current_user: dict = Depends(require_same_farm_or_super_admin)):
    table = get_table(TABLE_ALERT_STATE)
    response = table.query(
        KeyConditionExpression="farm_id = :f",
        ExpressionAttributeValues={":f": farm_id},
    )
    return response.get("Items", [])


@router.get("/{farm_id}/{alert_type}", response_model=AlertState)
def get_alert(farm_id: str, alert_type: str, current_user: dict = Depends(require_same_farm_or_super_admin)):
    table = get_table(TABLE_ALERT_STATE)
    response = table.get_item(Key={"farm_id": farm_id, "alert_type": alert_type})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="No alert state found")
    return item


@router.put("/{farm_id}/{alert_type}", response_model=AlertState)
def upsert_alert(
    farm_id: str,
    alert_type: str,
    payload: AlertUpdate,
    current_user: dict = Depends(require_same_farm_or_super_admin),
):
    if current_user["role"] == Role.STAFF.value:
        raise HTTPException(status_code=403, detail="Staff cannot modify alerts")
    if alert_type not in ALERT_TYPES:
        raise HTTPException(status_code=400, detail=f"alert_type must be one of {ALERT_TYPES}")
    return set_alert_state(farm_id, alert_type, payload.active, payload.message)


@router.post("/{farm_id}/{alert_type}/acknowledge", response_model=AlertState)
def acknowledge_alert(
    farm_id: str,
    alert_type: str,
    current_user: dict = Depends(require_same_farm_or_super_admin),
):
    if current_user["role"] == Role.STAFF.value:
        raise HTTPException(status_code=403, detail="Staff cannot acknowledge alerts")

    table = get_table(TABLE_ALERT_STATE)
    now = datetime.now(timezone.utc).isoformat()
    table.update_item(
        Key={"farm_id": farm_id, "alert_type": alert_type},
        UpdateExpression="SET acknowledged = :ack, acknowledged_by = :ab, acknowledged_at = :aa",
        ExpressionAttributeValues={
            ":ack": True,
            ":ab": current_user.get("user_id"),
            ":aa": now,
        },
    )
    response = table.get_item(Key={"farm_id": farm_id, "alert_type": alert_type})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="No alert state found")
    return item
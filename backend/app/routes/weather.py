"""
Weather routes.

GET  /weather/{farm_id}       - read the farm's last-synced weather snapshot
POST /weather/{farm_id}/sync  - fetch fresh weather now and store it

Access rules mirror alert_state (see services/permissions.py): super-admin any
farm; admin/staff only their own farm; staff read-only (cannot trigger a sync).
"""

from fastapi import APIRouter, HTTPException, Depends

from app.services.dynamo import get_table, TABLE_FARMS, TABLE_WEATHER
from app.services.weather import fetch_current_weather
from app.services.permissions import Role, require_same_farm_or_super_admin

router = APIRouter(prefix="/weather", tags=["weather"])


def sync_farm_weather(farm_id: str) -> dict:
    """Fetches live weather for a farm and stores it."""
    farm = get_table(TABLE_FARMS).get_item(Key={"farm_id": farm_id}).get("Item")
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    weather = fetch_current_weather(farm["latitude"], farm["longitude"])

    get_table(TABLE_WEATHER).put_item(Item={"farm_id": farm_id, "region": farm["region"], **weather})
    return weather


@router.get("/{farm_id}")
def get_weather(farm_id: str, current_user: dict = Depends(require_same_farm_or_super_admin)):
    item = get_table(TABLE_WEATHER).get_item(Key={"farm_id": farm_id}).get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="No weather data yet for this farm — trigger a sync first")
    return item


@router.post("/{farm_id}/sync")
def sync_weather(farm_id: str, current_user: dict = Depends(require_same_farm_or_super_admin)):
    if current_user["role"] == Role.STAFF.value:
        raise HTTPException(status_code=403, detail="Staff cannot trigger a weather sync")
    return sync_farm_weather(farm_id)

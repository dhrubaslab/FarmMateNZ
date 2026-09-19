"""
Paddocks routes.

Paddocks table uses a composite key: farm_id (partition) + paddock_id (sort).
paddock_id is only unique WITHIN a farm, not globally — e.g. "paddock-01"
exists under multiple farms — so every lookup needs both parts of the key.

Access rules:
- super-admin: view/edit/delete any paddock
- admin: view/edit their OWN farm's paddocks only
- staff: view their OWN farm's paddocks only (read-only)
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from decimal import Decimal
from boto3.dynamodb.conditions import Key
from app.services.dynamo import get_table, TABLE_PADDOCKS
from app.services.permissions import Role, require_roles, get_current_user

router = APIRouter(prefix="/paddocks", tags=["paddocks"])


class PaddockCreate(BaseModel):
    name: str
    farm_id: str
    area_hectares: float
    stock_type: str | None = None


class Paddock(PaddockCreate):
    paddock_id: str
    status: str = "active"


def _check_farm_access(current_user: dict, farm_id: str):
    if current_user["role"] != Role.SUPER_ADMIN.value and current_user.get("farm_id") != farm_id:
        raise HTTPException(status_code=403, detail="You do not have access to this farm's paddocks")


@router.post("", response_model=Paddock, dependencies=[Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN))])
def create_paddock(paddock: PaddockCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] == Role.ADMIN.value and paddock.farm_id != current_user["farm_id"]:
        raise HTTPException(status_code=403, detail="You can only create paddocks on your own farm")

    table = get_table(TABLE_PADDOCKS)
    paddock_id = f"paddock-{uuid.uuid4().hex[:8]}"
    item = {"paddock_id": paddock_id, "status": "active", **paddock.model_dump()}
    item["area_hectares"] = Decimal(str(item["area_hectares"]))
    table.put_item(Item=item)
    return item


@router.get("/{farm_id}/{paddock_id}", response_model=Paddock)
def get_paddock(farm_id: str, paddock_id: str, current_user: dict = Depends(get_current_user)):
    _check_farm_access(current_user, farm_id)
    table = get_table(TABLE_PADDOCKS)
    item = table.get_item(Key={"farm_id": farm_id, "paddock_id": paddock_id}).get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Paddock not found")
    return item


@router.get("")
def list_paddocks(current_user: dict = Depends(get_current_user)):
    table = get_table(TABLE_PADDOCKS)
    if current_user["role"] == Role.SUPER_ADMIN.value:
        items = table.scan().get("Items", [])
    else:
        # farm_id is the partition key, so a Query is both correct and
        # cheaper than a scan+filter for admin/staff scoped to one farm.
        response = table.query(KeyConditionExpression=Key("farm_id").eq(current_user["farm_id"]))
        items = response.get("Items", [])
    return items


@router.patch("/{farm_id}/{paddock_id}", response_model=Paddock)
def update_paddock(farm_id: str, paddock_id: str, paddock: PaddockCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] == Role.STAFF.value:
        raise HTTPException(status_code=403, detail="Staff cannot edit paddocks")
    _check_farm_access(current_user, farm_id)

    table = get_table(TABLE_PADDOCKS)
    existing = table.get_item(Key={"farm_id": farm_id, "paddock_id": paddock_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Paddock not found")

    update_values = {
        ":n": paddock.name,
        ":a": Decimal(str(paddock.area_hectares)),
        ":st": paddock.stock_type,
    }
    table.update_item(
        Key={"farm_id": farm_id, "paddock_id": paddock_id},
        UpdateExpression="SET #n = :n, area_hectares = :a, stock_type = :st",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues=update_values,
    )
    return {
        "farm_id": farm_id,
        "paddock_id": paddock_id,
        "status": existing.get("status", "active"),
        **paddock.model_dump(),
    }


@router.patch("/{farm_id}/{paddock_id}/status", dependencies=[Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN))])
def set_paddock_status(farm_id: str, paddock_id: str, status: str, current_user: dict = Depends(get_current_user)):
    if status not in ("active", "disabled"):
        raise HTTPException(status_code=400, detail="status must be 'active' or 'disabled'")
    _check_farm_access(current_user, farm_id)

    table = get_table(TABLE_PADDOCKS)
    existing = table.get_item(Key={"farm_id": farm_id, "paddock_id": paddock_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Paddock not found")

    table.update_item(
        Key={"farm_id": farm_id, "paddock_id": paddock_id},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": status},
    )
    return {"farm_id": farm_id, "paddock_id": paddock_id, "status": status}


@router.delete("/{farm_id}/{paddock_id}", dependencies=[Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN))])
def delete_paddock(farm_id: str, paddock_id: str, current_user: dict = Depends(get_current_user)):
    _check_farm_access(current_user, farm_id)
    table = get_table(TABLE_PADDOCKS)
    existing = table.get_item(Key={"farm_id": farm_id, "paddock_id": paddock_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Paddock not found")
    table.delete_item(Key={"farm_id": farm_id, "paddock_id": paddock_id})
    return {"message": "Paddock deleted"}
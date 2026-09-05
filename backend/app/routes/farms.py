"""
Farms routes.

Access rules:
- super-admin: create, edit, delete, enable/disable, view all farms
- admin: view/edit their OWN farm only
- staff: view their OWN farm only (read-only)
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from decimal import Decimal
from app.services.dynamo import get_table, TABLE_FARMS
from app.services.permissions import Role, require_roles, get_current_user

router = APIRouter(prefix="/farms", tags=["farms"])


class FarmCreate(BaseModel):
    name: str
    region: str
    size_hectares: float


class Farm(FarmCreate):
    farm_id: str
    status: str = "active"


@router.post("", response_model=Farm, dependencies=[Depends(require_roles(Role.SUPER_ADMIN))])
def create_farm(farm: FarmCreate):
    table = get_table(TABLE_FARMS)
    farm_id = f"farm-{uuid.uuid4().hex[:8]}"
    item = to_dynamo_safe({"farm_id": farm_id, "status": "active", **farm.model_dump()})
    table.put_item(Item=item)
    return item


@router.get("/{farm_id}", response_model=Farm)
def get_farm(farm_id: str, current_user: dict = Depends(get_current_user)):
    # super-admin can view any farm; admin/staff only their own
    if current_user["role"] != Role.SUPER_ADMIN.value and current_user.get("farm_id") != farm_id:
        raise HTTPException(status_code=403, detail="You do not have access to this farm")

    table = get_table(TABLE_FARMS)
    response = table.get_item(Key={"farm_id": farm_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Farm not found")
    return item


@router.get("")
def list_farms(current_user: dict = Depends(get_current_user)):
    table = get_table(TABLE_FARMS)
    if current_user["role"] == Role.SUPER_ADMIN.value:
        response = table.scan()
        return response.get("Items", [])
    else:
        # admin/staff only ever see their own single farm
        response = table.get_item(Key={"farm_id": current_user["farm_id"]})
        item = response.get("Item")
        return [item] if item else []


@router.patch("/{farm_id}", response_model=Farm)
def update_farm(farm_id: str, farm: FarmCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] == Role.STAFF.value:
        raise HTTPException(status_code=403, detail="Staff cannot edit farm profiles")
    if current_user["role"] == Role.ADMIN.value and current_user.get("farm_id") != farm_id:
        raise HTTPException(status_code=403, detail="You can only edit your own farm")

    table = get_table(TABLE_FARMS)
    table.update_item(
        Key={"farm_id": farm_id},
        UpdateExpression="SET #n = :n, #r = :r, size_hectares = :s",
        ExpressionAttributeNames={"#n": "name", "#r": "region"},
        ExpressionAttributeValues={
            ":n": farm.name,
            ":r": farm.region,
            ":s": Decimal(str(farm.size_hectares)),
        },
    )
    return {"farm_id": farm_id, "status": "active", **farm.model_dump()}


@router.patch("/{farm_id}/status", dependencies=[Depends(require_roles(Role.SUPER_ADMIN))])
def set_farm_status(farm_id: str, status: str):
    if status not in ("active", "disabled"):
        raise HTTPException(status_code=400, detail="status must be 'active' or 'disabled'")
    table = get_table(TABLE_FARMS)
    table.update_item(
        Key={"farm_id": farm_id},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": status},
    )
    return {"farm_id": farm_id, "status": status}


@router.delete("/{farm_id}", dependencies=[Depends(require_roles(Role.SUPER_ADMIN))])
def delete_farm(farm_id: str):
    table = get_table(TABLE_FARMS)
    table.delete_item(Key={"farm_id": farm_id})
    return {"message": "Farm deleted"}

def to_dynamo_safe(data: dict) -> dict:
    return {k: (Decimal(str(v)) if isinstance(v, float) else v) for k, v in data.items()}
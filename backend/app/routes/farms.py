"""
Farms routes — demonstrates the DynamoDB read/write pattern.
Schema matches db/init_dynamodb.py (farm_id, snake_case fields).
Other resources (Paddocks, Livestock, TaskLogs, AlertState) can follow
this same structure.
"""

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.dynamo import get_table, TABLE_FARMS

router = APIRouter(prefix="/farms", tags=["farms"])


class FarmCreate(BaseModel):
    name: str
    region: str
    size_hectares: float


class Farm(FarmCreate):
    farm_id: str


@router.post("", response_model=Farm)
def create_farm(farm: FarmCreate):
    table = get_table(TABLE_FARMS)
    farm_id = f"farm-{uuid.uuid4().hex[:8]}"
    item = {"farm_id": farm_id, **farm.model_dump()}
    table.put_item(Item=item)
    return item


@router.get("/{farm_id}", response_model=Farm)
def get_farm(farm_id: str):
    table = get_table(TABLE_FARMS)
    response = table.get_item(Key={"farm_id": farm_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Farm not found")
    return item


@router.get("")
def list_farms():
    table = get_table(TABLE_FARMS)
    response = table.scan()
    return response.get("Items", [])

"""
User routes — CRUD for the Users table.

Access rules:
- super-admin: view/edit/delete any user.
- admin: view/edit their OWN farm only; delete only their own staff.
- staff: no access, except resetting their own password.

User creation goes through POST /auth/invite, not this router.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.auth import hash_password
from app.services.dynamo import get_table, TABLE_USERS
from app.services.permissions import Role, require_roles, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


def _safe(user: dict) -> dict:
    """Never return the password hash."""
    return {k: v for k, v in user.items() if k != "hashed_password"}


class UserUpdate(BaseModel):
    name: str | None = None
    role: Role | None = None
    farm_id: str | None = None
    status: str | None = None


class PasswordReset(BaseModel):
    new_password: str


@router.get("", dependencies=[Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN))])
def list_users(current_user: dict = Depends(get_current_user)):
    table = get_table(TABLE_USERS)
    if current_user["role"] == Role.SUPER_ADMIN.value:
        items = table.scan().get("Items", [])
    else:
        # admin: only their own farm
        response = table.scan(
            FilterExpression="farm_id = :f",
            ExpressionAttributeValues={":f": current_user["farm_id"]},
        )
        items = response.get("Items", [])
    return [_safe(u) for u in items]


@router.get("/{user_id}", dependencies=[Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN))])
def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    table = get_table(TABLE_USERS)
    user = table.get_item(Key={"user_id": user_id}).get("Item")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user["role"] == Role.ADMIN.value and user.get("farm_id") != current_user["farm_id"]:
        raise HTTPException(status_code=403, detail="You do not have access to this user")
    return _safe(user)


@router.patch("/{user_id}", dependencies=[Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN))])
def update_user(user_id: str, payload: UserUpdate, current_user: dict = Depends(get_current_user)):
    table = get_table(TABLE_USERS)
    user = table.get_item(Key={"user_id": user_id}).get("Item")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user["role"] == Role.ADMIN.value:
        if user.get("farm_id") != current_user["farm_id"]:
            raise HTTPException(status_code=403, detail="You do not have access to this user")
        if payload.role is not None or payload.farm_id is not None:
            raise HTTPException(status_code=403, detail="Admins cannot change a user's role or farm")

    updates = {}
    if payload.name is not None:
        updates["name"] = payload.name
    if payload.role is not None:
        updates["role"] = payload.role.value
    if payload.farm_id is not None:
        updates["farm_id"] = payload.farm_id
    if payload.status is not None:
        updates["status"] = payload.status

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # alias every field — DynamoDB reserved words bit us before
    names, values, set_clauses = {}, {}, []
    for key, value in updates.items():
        names[f"#{key}"] = key
        values[f":{key}"] = value
        set_clauses.append(f"#{key} = :{key}")

    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="SET " + ", ".join(set_clauses),
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
    )
    updated = table.get_item(Key={"user_id": user_id}).get("Item")
    return _safe(updated)


@router.delete("/{user_id}", dependencies=[Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN))])
def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    table = get_table(TABLE_USERS)
    user = table.get_item(Key={"user_id": user_id}).get("Item")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user["role"] == Role.ADMIN.value:
        # same boundary as inviting
        if user.get("farm_id") != current_user["farm_id"]:
            raise HTTPException(status_code=403, detail="You do not have access to this user")
        if user.get("role") != Role.STAFF.value:
            raise HTTPException(status_code=403, detail="Admins can only delete staff accounts")

    table.delete_item(Key={"user_id": user_id})
    return {"message": "User deleted"}


@router.post("/{user_id}/reset-password")
def reset_password(user_id: str, payload: PasswordReset, current_user: dict = Depends(get_current_user)):
    """Sets a new password directly — no token or link needed."""
    is_self = current_user["user_id"] == user_id
    if not is_self and current_user["role"] not in (Role.SUPER_ADMIN.value, Role.ADMIN.value):
        raise HTTPException(status_code=403, detail="You can only reset your own password")

    table = get_table(TABLE_USERS)
    user = table.get_item(Key={"user_id": user_id}).get("Item")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not is_self and current_user["role"] == Role.ADMIN.value and user.get("farm_id") != current_user["farm_id"]:
        raise HTTPException(status_code=403, detail="You do not have access to this user")

    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="SET hashed_password = :p",
        ExpressionAttributeValues={":p": hash_password(payload.new_password)},
    )
    return {"message": "Password reset successfully"}

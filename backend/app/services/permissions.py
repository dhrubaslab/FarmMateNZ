"""
Roles and permission-checking dependencies for FastAPI routes.

Role summary (from project spec):

super-admin:
  - create/edit/delete/enable/disable Farm profiles
  - view all farms (not scoped to one farm)

admin (scoped to their own farm_id):
  - create staff profiles / send invite with reset-password link
  - view/edit own profile
  - view/edit farm profile
  - add/view/edit paddocks, livestock, task_logs
  - view alert_state

staff (scoped to their own farm_id):
  - view own profile
  - view farm profile, paddocks, livestock, task_logs, alert_state (read-only)
"""

from enum import Enum
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.services.auth import decode_access_token
from app.services.dynamo import get_table, TABLE_USERS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class Role(str, Enum):
    SUPER_ADMIN = "super-admin"
    ADMIN = "admin"
    STAFF = "staff"


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decodes the JWT and loads the current user's record from DynamoDB."""
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    table = get_table(TABLE_USERS)
    response = table.get_item(Key={"user_id": payload["user_id"]})
    user = response.get("Item")

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    return user


def require_roles(*allowed_roles: Role):
    """
    Dependency factory — restricts a route to specific roles.
    Usage: @router.post("/farms", dependencies=[Depends(require_roles(Role.SUPER_ADMIN))])
    """
    def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user['role']}' is not permitted to perform this action",
            )
        return current_user
    return checker


def require_same_farm_or_super_admin(farm_id: str, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Use for routes scoped by farm_id (paddocks, livestock, task_logs, alert_state).
    super-admin can access any farm; admin/staff can only access their own farm_id.
    """
    if current_user["role"] == Role.SUPER_ADMIN.value:
        return current_user
    if current_user.get("farm_id") != farm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this farm's data",
        )
    return current_user

"""
Auth routes: login, staff invitation, password reset.

Invite emails are sent via SNS in production. For local dev, the reset
link is printed to the console instead of actually emailing it.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.services.auth import hash_password, verify_password, create_access_token
from app.services.dynamo import get_table, TABLE_USERS
from app.services.permissions import Role, require_roles, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

SNS_TOPIC_ARN = os.getenv("SNS_INVITE_TOPIC_ARN")  # set in production; unset locally


# ---------- Schemas ----------

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    farm_id: str | None
    user_id: str


class InviteRequest(BaseModel):
    email: EmailStr
    name: str
    role: Role
    farm_id: str | None = None  # required for admin/staff, ignored for super-admin


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str


# ---------- Routes ----------

@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    table = get_table(TABLE_USERS)
    response = table.scan(
        FilterExpression="email = :e",
        ExpressionAttributeValues={":e": form_data.username},  # OAuth2 form uses "username" field for email
    )
    items = response.get("Items", [])
    if not items:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    user = items[0]
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if user.get("status") != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    token = create_access_token({"user_id": user["user_id"], "role": user["role"]})
    return LoginResponse(
        access_token=token,
        role=user["role"],
        farm_id=user.get("farm_id"),
        user_id=user["user_id"],
    )


@router.post("/invite", status_code=status.HTTP_201_CREATED)
def invite_user(
    invite: InviteRequest,
    current_user: dict = Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN)),
):
    # admin can only invite staff to their OWN farm; super-admin can invite anyone
    if current_user["role"] == Role.ADMIN.value:
        if invite.role != Role.STAFF:
            raise HTTPException(status_code=403, detail="Admins can only invite staff")
        invite.farm_id = current_user["farm_id"]  # force scope to admin's own farm

    table = get_table(TABLE_USERS)
    user_id = f"user-{uuid.uuid4().hex[:8]}"
    reset_token = uuid.uuid4().hex
    reset_expires = (datetime.now(timezone.utc) + timedelta(hours=48)).isoformat()

    item = {
        "user_id": user_id,
        "email": invite.email,
        "name": invite.name,
        "role": invite.role.value,
        "farm_id": invite.farm_id,
        "status": "invited",
        "hashed_password": "",  # set on reset-password completion
        "reset_token": reset_token,
        "reset_token_expires": reset_expires,
    }
    table.put_item(Item=item)

    reset_link = f"https://farmmate.nz/reset-password?token={reset_token}"

    if SNS_TOPIC_ARN:
        # Production: publish to SNS to actually send the invite email
        import boto3
        sns = boto3.client("sns")
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"You've been invited to FarmMate NZ. Set your password: {reset_link}",
            Subject="FarmMate NZ — You've been invited",
        )
    else:
        # Local dev: just print it so you can copy/paste the link to test
        print(f"[DEV] Invite link for {invite.email}: {reset_link}")

    return {"message": "Invite sent", "user_id": user_id}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    table = get_table(TABLE_USERS)
    response = table.scan(
        FilterExpression="reset_token = :t",
        ExpressionAttributeValues={":t": payload.reset_token},
    )
    items = response.get("Items", [])
    if not items:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = items[0]
    expires = datetime.fromisoformat(user["reset_token_expires"])
    if datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=400, detail="Reset token has expired")

    table.update_item(
        Key={"user_id": user["user_id"]},
        UpdateExpression="SET hashed_password = :p, #s = :active REMOVE reset_token, reset_token_expires",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":p": hash_password(payload.new_password),
            ":active": "active",
        },
    )
    return {"message": "Password set successfully. You can now log in."}


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    # never return hashed_password
    safe_user = {k: v for k, v in current_user.items() if k != "hashed_password"}
    return safe_user

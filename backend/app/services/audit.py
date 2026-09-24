import re
import uuid
from datetime import datetime, timezone

from fastapi import Request
from starlette.concurrency import run_in_threadpool

from app.services.auth import decode_access_token
from app.services.dynamo import get_table, TABLE_AUDIT_LOGS, TABLE_USERS

CHANGE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
SKIP_PATHS = {"/auth/login"}

ACTIONS = [
    ("POST", r"/auth/invite", "invited a new user"),
    ("POST", r"/auth/reset-password", "completed a password reset from an emailed link"),
    ("POST", r"/farms", "created a farm"),
    ("PATCH", r"/farms/([^/]+)", "updated farm {0}"),
    ("PATCH", r"/farms/([^/]+)/status", "changed the status of farm {0}"),
    ("DELETE", r"/farms/([^/]+)", "deleted farm {0}"),
    ("POST", r"/paddocks", "created a paddock"),
    ("PATCH", r"/paddocks/([^/]+)/([^/]+)", "updated paddock {1} on farm {0}"),
    ("PATCH", r"/paddocks/([^/]+)/([^/]+)/status", "changed the status of paddock {1} on farm {0}"),
    ("DELETE", r"/paddocks/([^/]+)/([^/]+)", "deleted paddock {1} on farm {0}"),
    ("PATCH", r"/users/([^/]+)", "updated user {0}"),
    ("DELETE", r"/users/([^/]+)", "deleted user {0}"),
    ("POST", r"/users/([^/]+)/reset-password", "reset the password of user {0}"),
    ("POST", r"/weather/([^/]+)/sync", "synced the weather for farm {0}"),
    ("PUT", r"/alerts/([^/]+)/([^/]+)", "set the {1} alert on farm {0}"),
    ("POST", r"/alerts/([^/]+)/([^/]+)/acknowledge", "acknowledged the {1} alert on farm {0}"),
]


def describe_change(who: str, actor_id: str | None, method: str, path: str, query: str) -> str:
    """Plain-English line, e.g. 'Super Admin (super-admin) deleted farm farm-009'."""
    action = f"made a {method} request to {path}"  # routes not listed above
    for action_method, pattern, text in ACTIONS:
        match = re.fullmatch(pattern, path)
        if action_method == method and match:
            action = text.format(*match.groups())
            break
    if actor_id and path == f"/users/{actor_id}/reset-password":
        action = "reset their own password"
    return f"{who} {action}" + (f" ({query})" if query else "")


def _find_user(user_id: str | None) -> dict:
    if not user_id:
        return {}
    return get_table(TABLE_USERS).get_item(Key={"user_id": user_id}).get("Item") or {}


def record_change(actor: dict, method: str, path: str, query: str, status_code: int):
    now = datetime.now(timezone.utc).isoformat()
    actor_id = actor.get("user_id")
    role = actor.get("role", "anonymous")
    user = _find_user(actor_id)
    if user.get("name"):
        who = f"{user['name']} ({role})"
    else:
        who = f"{role} {actor_id}" if actor_id else "Someone not signed in"

    item = {
        "log_type": "audit",
        "timestamp_id": f"{now}#{uuid.uuid4().hex[:8]}",
        "timestamp": now,
        "message": describe_change(who, actor_id, method, path, query),
        "actor_id": actor_id or "anonymous",
        "actor_role": role,
        "method": method,
        "path": path,
        "status_code": status_code,
    }
    if query:
        item["query"] = query
    if user.get("farm_id"):
        item["actor_farm_id"] = user["farm_id"]  # lets admins see their own farm's activity
    get_table(TABLE_AUDIT_LOGS).put_item(Item=item)


async def audit_middleware(request: Request, call_next):
    response = await call_next(request)
    if (
        request.method in CHANGE_METHODS
        and request.url.path not in SKIP_PATHS
        and response.status_code < 400
    ):
        try:
            token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
            actor = (decode_access_token(token) if token else None) or {}
            await run_in_threadpool(
                record_change, actor, request.method, request.url.path,
                request.url.query, response.status_code,
            )
        except Exception as exc:
            print(f"Audit log write failed: {exc}")  # never fail a request over logging
    return response

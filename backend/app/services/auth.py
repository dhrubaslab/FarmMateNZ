import json
import os
from datetime import datetime, timedelta, timezone

import boto3
from jose import JWTError, jwt
from passlib.context import CryptContext


def get_jwt_secret() -> str:
    secret_name = os.getenv("JWT_SECRET_NAME")

    if secret_name:
        client = boto3.client(
            "secretsmanager",
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )

        response = client.get_secret_value(
            SecretId=secret_name
        )

        secret_string = response["SecretString"]

        try:
            secret_data = json.loads(secret_string)
            return secret_data["FARM_MATE_APP_SECRET"]
        except (json.JSONDecodeError, KeyError):
            return secret_string

    # Local development fallback
    return os.getenv(
        "JWT_SECRET",
        "local-dev-secret-change-in-production"
    )


JWT_SECRET = get_jwt_secret()

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 8 hour session

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
    except JWTError as e:
        print("JWT DECODE ERROR:", type(e).__name__, str(e))
        return None

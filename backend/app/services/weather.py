"""
Weather service — fetches current conditions from Open-Meteo.

Open-Meteo is free and needs no API key, which is why it was picked over
NZ-specific providers (MetService/NIWA) that require registration.
"""

import json
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal
from app.services.alerts import set_alert_state

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_current_weather(lat, lon) -> dict:
    """Fetches current temperature and precipitation for a farm's coordinates."""
    url = (
        f"{OPEN_METEO_URL}?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,precipitation&timezone=Pacific%2FAuckland"
    )
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.load(response)

    current = data["current"]
    return {
        # DynamoDB's boto3 resource rejects native floats, so convert via str()
        # to avoid binary float imprecision (e.g. Decimal(9.4) != Decimal("9.4")).
        "temperature_celsius": Decimal(str(current["temperature_2m"])),
        "precipitation_mm": Decimal(str(current["precipitation"])),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import farms, auth, weather
from app.services.dynamo import get_table, TABLE_FARMS
from app.routes import alerts as alerts_routes


# How often the background job refreshes weather for every farm. Overridable
# via env var so it can be set low for a quick local demo instead of waiting
# an hour to see it run.
WEATHER_SYNC_INTERVAL_SECONDS = int(os.getenv("WEATHER_SYNC_INTERVAL_SECONDS", 60 * 60))


async def _weather_sync_loop():
    while True:
        try:
            all_farms = get_table(TABLE_FARMS).scan().get("Items", [])
            for farm in all_farms:
                try:
                    weather.sync_farm_weather(farm["farm_id"])
                except Exception as exc:
                    print(f"Weather sync failed for farm {farm['farm_id']}: {exc}")
        except Exception as exc:
            print(f"Weather sync loop error: {exc}")
        await asyncio.sleep(WEATHER_SYNC_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_weather_sync_loop())
    yield
    task.cancel()


app = FastAPI(title="FarmMate NZ API", lifespan=lifespan)

# Allow the local Vite dev server to call this API.
# In production, replace "*" origins with your actual deployed frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(farms.router)
app.include_router(weather.router)
app.include_router(alerts_routes.router)

@app.get("/health")
def health():
    return {"status": "ok"}

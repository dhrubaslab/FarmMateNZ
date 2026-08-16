from fastapi import FastAPI
from app.routes import farms

app = FastAPI(title="FarmMate NZ API")

app.include_router(farms.router)


@app.get("/health")
def health():
    return {"status": "ok"}
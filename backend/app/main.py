from fastapi import FastAPI
from app.routes import farms, auth

app = FastAPI(title="FarmMate NZ API")

app.include_router(auth.router)
app.include_router(farms.router)


@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import farms, auth

app = FastAPI(title="FarmMate NZ API")

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


@app.get("/health")
def health():
    return {"status": "ok"}

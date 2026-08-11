from fastapi import FastAPI

app = FastAPI(title="FarmMate NZ API")

@app.get("/health")
def health():
    return {"status": "ok"}
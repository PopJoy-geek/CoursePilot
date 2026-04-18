from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import recommendation, schedule

app = FastAPI(
    title="School Course Assistant",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    recommendation.router,
    prefix="/recommendations",
    tags=["recommendations"]
)

app.include_router(
    schedule.router,
    prefix="/schedules",
    tags=["schedules"]
)

@app.get("/")
def root():
    return {"message": "API running"}

@app.get("/health")
def health():
    return {"status": "ok"}
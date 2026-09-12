"""
AFH-DEMO FastAPI Application Entrypoint.
"""

from fastapi import FastAPI
from app.routes.auth import router as auth_router

app = FastAPI(
    title="AFH-DEMO Service",
    description="E-Commerce Core Microservice for AFH Testing",
    version="1.0.0"
)

app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "afh-demo"}

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, directory, patients
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(
    title=f"{settings.project_name} API",
    description="Synthetic-data healthcare platform for data engineering and DevOps learning.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(auth.router, prefix="/api/v1")
app.include_router(patients.router, prefix="/api/v1")
app.include_router(directory.router, prefix="/api/v1")


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    """Return a non-sensitive liveness response."""
    return {
        "status": "healthy",
        "service": "zambecare-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }

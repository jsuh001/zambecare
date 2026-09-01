from datetime import UTC, datetime

from fastapi import FastAPI

app = FastAPI(
    title="ZambeCare API",
    description="Synthetic-data healthcare platform for data engineering and DevOps learning.",
    version="0.1.0",
)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    """Return a non-sensitive liveness response."""
    return {
        "status": "healthy",
        "service": "zambecare-api",
        "timestamp": datetime.now(UTC).isoformat(),
    }

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import vouchers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create database tables on startup.

    Uses asyncio.to_thread to run synchronous database operations
    in a thread pool, making it properly async.
    """
    await asyncio.to_thread(Base.metadata.create_all, bind=engine)
    yield


app = FastAPI(
    title="Voucher Management API",
    description="A simple REST API for managing discount vouchers",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(vouchers.router)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}

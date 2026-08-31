from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.logger import configure_logging
from backend.auth import router as auth_router
from backend.history import router as history_router
from backend.routers.documents import router as documents_router


configure_logging()

logger = logging.getLogger(__name__)
logger.info("BACKEND_STARTED")

app = FastAPI(title="RAG Document QA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(history_router)
app.include_router(documents_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    logger.info("HEALTH_CHECK | status=healthy")
    return {"status": "healthy"}
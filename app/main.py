import time
from collections import defaultdict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import Base, engine
from app.db import models  # noqa: F401  ensures models are registered

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="GARUDA — Genetic Analysis, Research, Understanding, Design & Assessment platform API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- simple in-memory rate limiter (per-IP, sliding window) ---
RATE_LIMIT = 60  # requests
RATE_WINDOW = 60  # seconds
_request_log: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    log = _request_log[client_ip]
    _request_log[client_ip] = [t for t in log if now - t < RATE_WINDOW]

    if len(_request_log[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please slow down."},
        )

    _request_log[client_ip].append(now)
    return await call_next(request)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME}


app.include_router(api_router, prefix=settings.API_V1_STR)

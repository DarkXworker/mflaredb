"""
MovieFlare — FastAPI Application Entry Point
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.middleware.security import SecurityMiddleware
from app.routes.api import router as api_router
from app.routes.admin_api import router as admin_router
from app.utils.cache import close_redis
from admin.routes import router as admin_panel_router

# Logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 MovieFlare backend starting...")
    await init_db()
    logger.info("✅ Database initialized")
    yield
    # Shutdown
    await close_redis()
    logger.info("👋 MovieFlare backend stopped")


app = FastAPI(
    title="MovieFlare API",
    version="1.0.0",
    description="Secure streaming backend",
    docs_url="/docs" if settings.DEBUG else None,  # Disable Swagger in production
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [
        "https://movieflare.com",
        "https://www.movieflare.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ─── Security Middleware ─────────────────────────────────────
app.add_middleware(SecurityMiddleware)

# ─── Routes ──────────────────────────────────────────────────
app.include_router(api_router)           # /api/*
app.include_router(admin_router)         # /admin/* (REST API)
app.include_router(admin_panel_router)   # /admin   (HTML panel)

# ─── Static files (frontend) ─────────────────────────────────
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


# ─── Health Check ────────────────────────────────────────────
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "service": "MovieFlare"})


@app.get("/")
async def root():
    return JSONResponse({"message": "MovieFlare API", "version": "1.0.0"})

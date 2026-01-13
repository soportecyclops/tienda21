"""
Archivo: app/main.py

Utilidad:
---------
Punto de entrada principal del bot comercial JARVIS.
Inicializa FastAPI, lifecycle, middlewares y routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.gateway.router import webhook_router
from app.observability.logger import setup_logging
from app.observability.metrics import setup_metrics
from app.context.store import init_db

# ------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------

setup_logging()
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Lifespan
# ------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    logger.info("Iniciando bot comercial JARVIS...")

    await init_db()
    logger.info("Base de datos inicializada")

    setup_metrics()
    logger.info("Sistema de métricas configurado")

    yield

    logger.info("Apagando bot comercial JARVIS...")


# ------------------------------------------------------------------
# App
# ------------------------------------------------------------------

app = FastAPI(
    title="JARVIS Commercial Bot",
    description="Bot comercial para el ecosistema JARVIS",
    version="1.0.0",
    lifespan=lifespan,
)

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Routers
# ------------------------------------------------------------------

# Router CANÓNICO (NO duplicar, NO versionar aún)
app.include_router(webhook_router)


# ------------------------------------------------------------------
# Health & Root
# ------------------------------------------------------------------

@app.get("/")
async def root():
    return {"status": "online", "service": "JARVIS Commercial Bot"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "database": "operational",
            "llm": "connected",
            "rules_engine": "active",
        },
    }


# ------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

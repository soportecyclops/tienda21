"""
Archivo: app/api/v1/webhook.py


Router versionado v1.
Contrato: delega 100% en el router canónico sin duplicar lógica.
"""


from fastapi import APIRouter
from app.gateway.router import webhook_router as canonical_webhook_router


# Router v1
router = APIRouter(prefix="/api/v1")


# Montamos el router canónico debajo de /api/v1
router.include_router(canonical_webhook_router)
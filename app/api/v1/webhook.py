"""
Archivo: app/api/v1/webhook.py

Capa API v1.
Expone endpoints HTTP versionados.

Ley:
- NO lógica
- NO validación de negocio
- Reexporta routers canónicos
"""

from app.gateway.router import webhook_router as router

__all__ = ["router"]

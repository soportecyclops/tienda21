"""
Archivo: app/gateway/router.py

Router del subsistema Gateway.
Punto de entrada HTTP para:
- Chat (usuarios)
- Webhooks externos (Tienda Nube)

Leyes:
------
- El router NO contiene lógica de negocio.
- Orquesta subsistemas.
- Debe ser completamente mockeable por tests.
"""

from typing import Dict, Any, Optional
import inspect

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer

from app.config import settings
from app.gateway.security import verify_webhook_signature
from app.session.manager import SessionManager
from app.rules.engine import RulesEngine
from app.llm.adapter import LLMAdapter
from app.responses.generator import ResponseGenerator
from app.observability.metrics import track_webhook_received
from app.observability.logger import get_logger

logger = get_logger(__name__)
security = HTTPBearer()

# Router CANÓNICO
webhook_router = APIRouter(
    prefix="/webhook",
    tags=["gateway"],
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def _call_maybe_async(func, *args, **kwargs):
    """
    Permite llamar funciones sync o async de forma uniforme.
    Fundamental para compatibilidad con mocks de pytest.
    """
    result = func(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


# ------------------------------------------------------------------
# Webhooks externos
# ------------------------------------------------------------------

@webhook_router.post("/tiendanube")
async def tiendanube_webhook(
    request: Request,
    token: str = Depends(security),
) -> Dict[str, Any]:
    try:
        payload = await request.json()
        event_type = request.headers.get("x-event-type")

        track_webhook_received("tiendanube", event_type)

        if not verify_webhook_signature(
            request.headers.get("x-signature"),
            await request.body(),
            settings.TIENDANUBE_WEBHOOK_SECRET,
        ):
            raise HTTPException(status_code=401, detail="Firma inválida")

        if event_type == "order/created":
            await process_new_order(payload)
        elif event_type == "product/updated":
            await process_product_update(payload)
        else:
            logger.warning(f"Evento Tienda Nube no manejado: {event_type}")

        return {"status": "processed", "event": event_type}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error procesando webhook Tienda Nube")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor",
        )


# ------------------------------------------------------------------
# Chat
# ------------------------------------------------------------------

@webhook_router.post("/chat")
async def chat_webhook(
    request: Request,
    token: str = Depends(security),
) -> Dict[str, Any]:
    try:
        payload = await request.json()
        user_id: Optional[str] = payload.get("user_id")
        message: Optional[str] = payload.get("message")

        if not user_id or not message:
            raise HTTPException(
                status_code=400,
                detail="Faltan datos requeridos",
            )

        track_webhook_received("chat", "message")

        session_manager = SessionManager()
        session = await _call_maybe_async(
            session_manager.get_or_create_session,
            user_id,
        )

        rules_engine = RulesEngine()
        rule_result = await _call_maybe_async(
            rules_engine.check_message,
            message,
            session,
        )

        if rule_result.is_violation:
            response = rule_result.response
        else:
            llm = LLMAdapter()
            llm_output = await _call_maybe_async(
                llm.process_message,
                message,
                session,
            )

            generator = ResponseGenerator()
            response = await _call_maybe_async(
                generator.generate,
                llm_output,
                session,
            )

        await _call_maybe_async(
            session_manager.update_session,
            session,
            message,
            response,
        )

        return {"response": response}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error procesando mensaje de chat")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor",
        )


# ------------------------------------------------------------------
# Stubs expuestos (mockeables)
# ------------------------------------------------------------------

async def process_new_order(payload: Dict[str, Any]) -> None:
    logger.info(f"Nuevo pedido recibido: {payload.get('id')}")


async def process_product_update(payload: Dict[str, Any]) -> None:
    logger.info(f"Producto actualizado: {payload.get('id')}")

"""
Archivo: app/gateway/router.py

Router del subsistema Gateway.
Punto de entrada de webhooks externos (chat y Tienda Nube).

Este archivo NO contiene lógica de negocio.
"""

from typing import Dict, Any, Callable
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

# Router CANÓNICO (contrato con app.main y tests)
webhook_router = APIRouter(
    prefix="/webhook",
    tags=["gateway"],
)

# Alias interno
router = webhook_router


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def _call_maybe_async(func: Callable, *args, **kwargs):
    result = func(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


# ------------------------------------------------------------------
# Webhooks
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
            logger.warning(f"Evento no manejado: {event_type}")

        return {"status": "processed", "event": event_type}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error procesando webhook Tienda Nube")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@webhook_router.post("/chat")
async def chat_webhook(
    request: Request,
    token: str = Depends(security),
) -> Dict[str, Any]:
    try:
        payload = await request.json()
        user_id = payload.get("user_id")
        message = payload.get("message")

        if not user_id or not message:
            raise HTTPException(status_code=400, detail="Faltan datos requeridos")

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
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# ------------------------------------------------------------------
# Stubs EXPUESTOS (mockeables)
# ------------------------------------------------------------------

async def process_new_order(payload: Dict[str, Any]) -> None:
    logger.info(f"Nuevo pedido recibido: {payload.get('id')}")


async def process_product_update(payload: Dict[str, Any]) -> None:
    logger.info(f"Producto actualizado: {payload.get('id')}")

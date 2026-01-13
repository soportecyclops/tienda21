from fastapi import APIRouter, Depends
from app.api.v1.schemas import (
WebhookChatPayload,
WebhookTiendaNubePayload,
)
from app.gateway.router import handle_chat, handle_tiendanube


router = APIRouter(prefix="/webhook", tags=["webhook"])




@router.post("/chat")
async def chat_webhook(payload: WebhookChatPayload):
return await handle_chat(payload)




@router.post("/tiendanube")
async def tiendanube_webhook(payload: WebhookTiendaNubePayload):
return await handle_tiendanube(payload)
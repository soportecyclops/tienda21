"""
Archivo: app/api/v1/schemas.py

Esquemas de entrada/salida para la API v1.
Contratos estrictos: NO se permiten campos extra.
"""

from pydantic import BaseModel, ConfigDict


class WebhookChatPayload(BaseModel):
    """
    Payload esperado para el webhook de chat.
    """

    user_id: str
    message: str

    # Pydantic v2: configuración del modelo
    model_config = ConfigDict(
        extra="forbid",   # ❌ rechaza campos no definidos
        str_strip_whitespace=True,
        validate_assignment=True,
    )

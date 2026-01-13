"""
Modelos de datos para gestión de sesiones.
Define esquemas y enums para sesiones y mensajes.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SessionState(str, Enum):
    """Estados posibles de una sesión."""
    ACTIVE = "active"
    IDLE = "idle"
    CLOSED = "closed"
    ESCALATED = "escalated"


class MessageRole(str, Enum):
    """Roles posibles en un mensaje."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Modelo para un mensaje en la conversación."""
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Session(BaseModel):
    """Modelo para una sesión de usuario."""
    session_id: str
    user_id: str
    state: SessionState = SessionState.ACTIVE
    created_at: datetime
    last_access: datetime
    messages: List[Message] = []
    context: Dict[str, Any] = {}
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionCreate(BaseModel):
    """Modelo para crear una nueva sesión."""
    user_id: str
    initial_context: Optional[Dict[str, Any]] = None


class SessionUpdate(BaseModel):
    """Modelo para actualizar una sesión existente."""
    state: Optional[SessionState] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(BaseModel):
    """Modelo para crear un nuevo mensaje."""
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None
"""
Ruta: app/context/store.py

Store in-memory de sesiones.
Contrato:
- Una sesión CLOSED no es retornable
- Expiración = eliminación lógica del store
- Expone init_db() por compatibilidad con el core
"""

from typing import Dict, Optional
from app.session.models import Session, SessionState

_SESSIONS: Dict[str, Session] = {}


async def init_db() -> None:
    """
    Hook de inicialización del store.
    En implementación in-memory no hace nada,
    pero se mantiene por contrato con app.main.
    """
    _SESSIONS.clear()


async def get_session(user_id: str) -> Optional[Session]:
    session = _SESSIONS.get(user_id)

    if not session:
        return None

    # 🔒 Regla dura: sesiones cerradas no existen
    if session.state != SessionState.ACTIVE:
        _SESSIONS.pop(user_id, None)
        return None

    return session


async def save_session(session: Session) -> None:
    if session.state == SessionState.CLOSED:
        # ❌ No persistir sesiones muertas
        _SESSIONS.pop(session.user_id, None)
        return

    _SESSIONS[session.user_id] = session

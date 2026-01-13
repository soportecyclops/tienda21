"""
Ruta: app/session/manager.py

Gestor del ciclo de vida de sesiones.
Contrato: una sesión expirada JAMÁS se reutiliza.
"""

import uuid
from datetime import datetime, timedelta

from app.session.models import Session, SessionState, Message, MessageRole
from app.context.store import get_session, save_session
from app.observability.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


class SessionManager:
    def __init__(self):
        self.timeout_minutes = settings.SESSION_TIMEOUT_MINUTES

    async def get_or_create_session(self, user_id: str) -> Session:
        existing_session = await get_session(user_id)

        if existing_session:
            if self._is_session_valid(existing_session):
                # Sesión válida → refrescar y devolver
                existing_session.last_access = datetime.now()
                await save_session(existing_session)
                return existing_session

            # ⚠️ Sesión expirada → cierre duro
            existing_session.state = SessionState.CLOSED
            await save_session(existing_session)

        # Siempre crear nueva si:
        # - no existe
        # - o la existente expiró
        return await self._create_new_session(user_id)

    async def update_session(
        self,
        session: Session,
        user_message: str,
        bot_response: str,
    ) -> Session:
        session.messages.append(
            Message(
                role=MessageRole.USER,
                content=user_message,
                timestamp=datetime.now(),
            )
        )

        session.messages.append(
            Message(
                role=MessageRole.ASSISTANT,
                content=bot_response,
                timestamp=datetime.now(),
            )
        )

        session.last_access = datetime.now()
        await save_session(session)
        return session

    async def close_session(self, user_id: str) -> bool:
        session = await get_session(user_id)
        if not session:
            return False

        session.state = SessionState.CLOSED
        await save_session(session)
        return True

    async def _create_new_session(self, user_id: str) -> Session:
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            state=SessionState.ACTIVE,
            created_at=datetime.now(),
            last_access=datetime.now(),
            messages=[],
            context={},
            metadata=None,
        )

        await save_session(session)
        logger.info(f"Nueva sesión creada: {session.session_id}")
        return session

    def _is_session_valid(self, session: Session) -> bool:
        if session.state != SessionState.ACTIVE:
            return False

        expiration = session.last_access + timedelta(minutes=self.timeout_minutes)
        return datetime.now() <= expiration

"""
Tests para el gestor de sesiones.
Verifica el funcionamiento del gestor de estado de sesión.
"""

import pytest
from datetime import datetime, timedelta

from app.session.manager import SessionManager
from app.session.models import Session, SessionState, Message, MessageRole


@pytest.fixture
def session_manager():
    """Fixture para crear una instancia del gestor de sesiones."""
    return SessionManager()


@pytest.fixture
def sample_user_id():
    """Fixture para proporcionar un ID de usuario de ejemplo."""
    return "test_user_123"


@pytest.mark.asyncio
async def test_create_new_session(session_manager, sample_user_id):
    """Test para crear una nueva sesión."""
    session = await session_manager.get_or_create_session(sample_user_id)
    
    assert session.user_id == sample_user_id
    assert session.state == SessionState.ACTIVE
    assert len(session.messages) == 0
    assert session.session_id is not None


@pytest.mark.asyncio
async def test_get_existing_session(session_manager, sample_user_id):
    """Test para obtener una sesión existente."""
    # Crear sesión inicial
    initial_session = await session_manager.get_or_create_session(sample_user_id)
    initial_session_id = initial_session.session_id
    
    # Obtener la misma sesión
    retrieved_session = await session_manager.get_or_create_session(sample_user_id)
    
    assert retrieved_session.session_id == initial_session_id
    assert retrieved_session.user_id == sample_user_id
    assert retrieved_session.state == SessionState.ACTIVE


@pytest.mark.asyncio
async def test_update_session(session_manager, sample_user_id):
    """Test para actualizar una sesión con nuevos mensajes."""
    # Crear sesión
    session = await session_manager.get_or_create_session(sample_user_id)
    
    # Actualizar sesión con mensajes
    user_message = "¿Cuál es el precio del producto X?"
    bot_response = "El precio del producto X es $99.99."
    
    updated_session = await session_manager.update_session(
        session,
        user_message,
        bot_response
    )
    
    assert len(updated_session.messages) == 2
    assert updated_session.messages[0].content == user_message
    assert updated_session.messages[0].role == MessageRole.USER
    assert updated_session.messages[1].content == bot_response
    assert updated_session.messages[1].role == MessageRole.ASSISTANT


@pytest.mark.asyncio
async def test_close_session(session_manager, sample_user_id):
    """Test para cerrar una sesión."""
    # Crear sesión
    session = await session_manager.get_or_create_session(sample_user_id)
    assert session.state == SessionState.ACTIVE
    
    # Cerrar sesión
    result = await session_manager.close_session(sample_user_id)
    assert result == True
    
    # Verificar que la sesión está cerrada
    closed_session = await session_manager.get_or_create_session(sample_user_id)
    # Debería crear una nueva sesión porque la anterior está cerrada
    assert closed_session.session_id != session.session_id


@pytest.mark.asyncio
async def test_session_timeout(session_manager, sample_user_id):
    """Test para verificar el tiempo de espera de sesión."""
    # Crear sesión
    session = await session_manager.get_or_create_session(sample_user_id)
    
    # Simular que la sesión ha expirado
    session.last_access = datetime.now() - timedelta(minutes=session_manager.timeout_minutes + 1)
    
    # Intentar obtener la sesión (debería crear una nueva)
    new_session = await session_manager.get_or_create_session(sample_user_id)
    
    # Debería ser una nueva sesión porque la anterior expiró
    assert new_session.session_id != session.session_id
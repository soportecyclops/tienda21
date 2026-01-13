"""
Tests para el gateway de webhooks.
Verifica el funcionamiento del receptor y procesamiento de webhooks.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.gateway.security import verify_webhook_signature


@pytest.fixture
def client():
    """Fixture para crear un cliente de prueba."""
    return TestClient(app)


@pytest.fixture
def sample_webhook_payload():
    """Fixture para proporcionar un payload de webhook de ejemplo."""
    return {
        "id": "12345",
        "event": "order.created",
        "data": {
            "order_id": "ORD12345",
            "customer_id": "CUST123",
            "total": 99.99
        }
    }


def test_root_endpoint(client):
    """Test para el endpoint raíz."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_health_endpoint(client):
    """Test para el endpoint de salud."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch('app.gateway.router.verify_webhook_signature')
@patch('app.gateway.router.process_new_order')
def test_tiendanube_webhook(mock_process_order, mock_verify_signature, client, sample_webhook_payload):
    """Test para el endpoint de webhook de Tienda Nube."""
    # Configurar mocks
    mock_verify_signature.return_value = True
    mock_process_order.return_value = None
    
    # Enviar webhook
    response = client.post(
        "/webhook/tiendanube",
        json=sample_webhook_payload,
        headers={
            "Authorization": "Bearer test_token",
            "x-signature": "test_signature",
            "x-event-type": "order/created"
        }
    )
    
    # Verificar respuesta
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert response.json()["event"] == "order/created"
    
    # Verificar que se llamó a la función de procesamiento
    mock_process_order.assert_called_once_with(sample_webhook_payload)


@patch('app.gateway.router.verify_webhook_signature')
def test_tiendanube_webhook_invalid_signature(mock_verify_signature, client, sample_webhook_payload):
    """Test para webhook con firma inválida."""
    # Configurar mock
    mock_verify_signature.return_value = False
    
    # Enviar webhook
    response = client.post(
        "/webhook/tiendanube",
        json=sample_webhook_payload,
        headers={
            "Authorization": "Bearer test_token",
            "x-signature": "invalid_signature",
            "x-event-type": "order/created"
        }
    )
    
    # Verificar respuesta
    assert response.status_code == 401
    assert response.json()["detail"] == "Firma inválida"


@patch('app.gateway.router.SessionManager')
@patch('app.gateway.router.RulesEngine')
@patch('app.gateway.router.LLMAdapter')
@patch('app.gateway.router.ResponseGenerator')
def test_chat_webhook(mock_response_generator, mock_llm_adapter, mock_rules_engine, mock_session_manager, client):
    """Test para el endpoint de chat."""
    # Configurar mocks
    mock_session = AsyncMock()
    mock_session.messages = []
    mock_session_manager.return_value.get_or_create_session.return_value = mock_session
    mock_session_manager.return_value.update_session.return_value = mock_session
    
    mock_rule_result = AsyncMock()
    mock_rule_result.is_violation = False
    mock_rules_engine.return_value.check_message.return_value = mock_rule_result
    
    mock_llm_adapter.return_value.process_message.return_value = "Respuesta del bot"
    
    mock_generator = AsyncMock()
    mock_generator.generate.return_value = "Respuesta final"
    mock_response_generator.return_value = mock_generator
    
    # Enviar mensaje de chat
    response = client.post(
        "/webhook/chat",
        json={
            "user_id": "test_user",
            "message": "Hola, ¿cómo estás?"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Verificar respuesta
    assert response.status_code == 200
    assert response.json()["response"] == "Respuesta final"


def test_chat_webhook_missing_data(client):
    """Test para webhook de chat con datos faltantes."""
    # Enviar mensaje sin user_id
    response = client.post(
        "/webhook/chat",
        json={
            "message": "Hola, ¿cómo estás?"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Verificar respuesta
    assert response.status_code == 400
    assert response.json()["detail"] == "Faltan datos requeridos"


def test_verify_webhook_signature():
    """Test para la función de verificación de firma."""
    # Datos de prueba
    payload = b'{"test": "data"}'
    secret = "test_secret"
    
    # Generar firma válida
    import hmac
    import hashlib
    valid_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Verificar firma válida
    assert verify_webhook_signature(valid_signature, payload, secret) == True
    
    # Verificar firma inválida
    assert verify_webhook_signature("invalid_signature", payload, secret) == False
    
    # Verificar con datos faltantes
    assert verify_webhook_signature(None, payload, secret) == False
    assert verify_webhook_signature(valid_signature, payload, None) == False
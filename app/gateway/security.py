"""
Módulo de seguridad para validación de firmas y autenticación.
Implementa mecanismos de verificación de integridad de mensajes.
"""

import hmac
import hashlib
from typing import Optional
import logging

from app.observability.logger import get_logger

logger = get_logger(__name__)


def verify_webhook_signature(
    signature: Optional[str],
    payload: bytes,
    secret: Optional[str]
) -> bool:
    """
    Verifica la firma de un webhook utilizando HMAC.
    
    Args:
        signature: Firma recibida en el header
        payload: Cuerpo del mensaje en bytes
        secret: Secreto compartido para verificar la firma
        
    Returns:
        bool: True si la firma es válida, False en caso contrario
    """
    if not signature or not secret:
        logger.warning("Firma o secreto no proporcionados")
        return False
    
    try:
        # Calcular firma esperada
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Comparar firmas (usando hmac.compare_digest para evitar timing attacks)
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logger.warning("Firma inválida detectada")
        
        return is_valid
    
    except Exception as e:
        logger.error(f"Error verificando firma: {str(e)}")
        return False


def validate_api_key(api_key: Optional[str], expected_key: Optional[str]) -> bool:
    """
    Valida una API key.
    
    Args:
        api_key: API key recibida
        expected_key: API key esperada
        
    Returns:
        bool: True si la API key es válida, False en caso contrario
    """
    if not api_key or not expected_key:
        return False
    
    return hmac.compare_digest(api_key, expected_key)
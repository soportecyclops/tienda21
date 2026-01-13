"""
Utilidades para generación y manejo de IDs.
Implementa funciones para crear IDs únicos y validarlos.
"""

import uuid
import random
import string
from typing import Optional


def generate_uuid() -> str:
    """
    Genera un UUID único.
    
    Returns:
        str: UUID generado
    """
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    Genera un ID corto alfanumérico.
    
    Args:
        length: Longitud del ID
        
    Returns:
        str: ID corto generado
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_session_id() -> str:
    """
    Genera un ID de sesión único.
    
    Returns:
        str: ID de sesión generado
    """
    return f"sess_{generate_short_id(12)}"


def generate_request_id() -> str:
    """
    Genera un ID de solicitud único.
    
    Returns:
        str: ID de solicitud generado
    """
    return f"req_{generate_short_id(16)}"


def generate_order_id() -> str:
    """
    Genera un ID de pedido único.
    
    Returns:
        str: ID de pedido generado
    """
    timestamp = int(time.time())
    random_part = generate_short_id(6)
    return f"ORD{timestamp}{random_part}"


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Verifica si una cadena es un UUID válido.
    
    Args:
        uuid_string: Cadena a verificar
        
    Returns:
        bool: True si es un UUID válido, False en caso contrario
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def extract_id_from_string(s: str, prefix: str) -> Optional[str]:
    """
    Extrae un ID de una cadena con un prefijo específico.
    
    Args:
        s: Cadena que contiene el ID
        prefix: Prefijo del ID
        
    Returns:
        Optional[str]: ID extraído o None si no se encuentra
    """
    if s.startswith(prefix):
        return s[len(prefix):]
    return None


# Importar time aquí para evitar dependencias circulares
import time
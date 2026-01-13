"""
Patrones y expresiones regulares para validación de contenido.
"""

from typing import Dict, Pattern
import re


def get_patterns() -> Dict[str, Pattern]:
    return {
        "greeting": re.compile(r"\b(hola|hey|buen(os|as))\b", re.IGNORECASE),
        "farewell": re.compile(r"\b(adiós|chau|bye|hasta luego)\b", re.IGNORECASE),
        "thanks": re.compile(r"\b(gracias|te agradezco)\b", re.IGNORECASE),
        "help": re.compile(r"\b(ayuda|necesito ayuda|cómo funciona)\b", re.IGNORECASE),
        "product_query": re.compile(r"\b(producto|precio|comprar|catálogo)\b", re.IGNORECASE),
        "order_status": re.compile(r"\b(pedido|seguimiento|envío)\b", re.IGNORECASE),
        "support": re.compile(r"\b(soporte|problema|no funciona)\b", re.IGNORECASE),
    }


def get_forbidden_patterns() -> Dict[str, Pattern]:
    return {
        "discrimination": re.compile(
            r"\b(discriminatorio|racista|sexista|homofóbico|odio)\b",
            re.IGNORECASE,
        ),
        "profanity": re.compile(
            r"\b(mierda|idiota|imbécil|estúpido)\b",
            re.IGNORECASE,
        ),
        "illegal": re.compile(
            r"\b(drogas|armas|robar|fraude)\b",
            re.IGNORECASE,
        ),
        "personal_data": re.compile(
            r"\b(dni|documento|contraseña|tarjeta)\b",
            re.IGNORECASE,
        ),
    }


def get_response_templates() -> Dict[str, str]:
    return {
        "forbidden_content": "No puedo procesar ese tipo de solicitud.",
        "unknown": "No estoy seguro de entender. ¿Podrías reformular?",
    }

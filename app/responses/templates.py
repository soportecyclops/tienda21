"""
Plantillas de respuestas estáticas.
Define respuestas predefinidas para situaciones comunes.
"""

from typing import Dict


def get_template(template_name: str) -> str:
    """
    Obtiene una plantilla de respuesta por nombre.
    
    Args:
        template_name: Nombre de la plantilla
        
    Returns:
        str: Plantilla de respuesta
    """
    templates = {
        "greeting": "¡Hola! Soy el asistente virtual de JARVIS. ¿En qué puedo ayudarte hoy?",
        "farewell": "¡Hasta luego! No dudes en volver si necesitas algo más.",
        "thanks": "¡De nada! Estoy aquí para ayudarte. ¿Hay algo más en lo que pueda asistirte?",
        "help": "Puedo ayudarte a buscar productos, verificar el estado de tu pedido o responder preguntas sobre nuestros servicios. ¿Qué necesitas?",
        "product_query": "Puedo ayudarte a encontrar productos en nuestro catálogo. ¿Qué estás buscando?",
        "order_status": "Para consultar el estado de tu pedido, necesito tu número de pedido. ¿Puedes proporcionarlo?",
        "support": "Entiendo que necesitas ayuda técnica. Te transferiré con un especialista en breve.",
        "forbidden_content": "No puedo procesar ese tipo de solicitud. ¿Hay algo más en lo que pueda ayudarte?",
        "unknown": "No estoy seguro de entender. ¿Podrías reformular tu pregunta?",
        "error": "Lo siento, tuve un problema al procesar tu solicitud. ¿Podrías intentarlo de nuevo?",
        "escalation": "Entiendo que necesitas ayuda especializada. Te transferiré con un operador humano en breve.",
        "no_results": "No encontré resultados para tu búsqueda. ¿Podrías intentar con otros términos?",
        "out_of_stock": "Lo siento, ese producto está agotado actualmente. ¿Te gustaría que te avise cuando esté disponible?",
        "payment_issue": "Parece que hay un problema con el pago. ¿Podrías verificar tu información de pago o intentar con otro método?",
        "shipping_info": "Los envíos se realizan dentro de las 24-48 horas hábiles. El tiempo de entrega varía según tu ubicación."
    }
    
    return templates.get(template_name, "Respuesta no encontrada.")


def get_product_template() -> str:
    """
    Obtiene la plantilla para mostrar información de un producto.
    
    Returns:
        str: Plantilla de producto
    """
    return """
**{name}**
Precio: ${price}
Descripción: {description}
Stock: {stock} unidades disponibles

¿Te gustaría agregar este producto a tu carrito?
    """.strip()


def get_order_template() -> str:
    """
    Obtiene la plantilla para mostrar el estado de un pedido.
    
    Returns:
        str: Plantilla de pedido
    """
    return """
**Pedido #{id}**
Estado: {status}

Productos:
{items}

Total: ${total}

Entrega estimada: {estimated_delivery}

¿Hay algo más que quieras saber sobre tu pedido?
    """.strip()


def get_handoff_template() -> str:
    """
    Obtiene la plantilla para informar sobre un escalamiento.
    
    Returns:
        str: Plantilla de escalamiento
    """
    return """
Entiendo que necesitas ayuda especializada. He solicitado que un operador humano se comunique contigo lo antes posible.

Tiempo de espera estimado: 5-10 minutos

Mientras tanto, ¿hay algo más en lo que pueda ayudarte?
    """.strip()


def get_error_template(error_type: str) -> str:
    """
    Obtiene una plantilla de error específica.
    
    Args:
        error_type: Tipo de error
        
    Returns:
        str: Plantilla de error
    """
    error_templates = {
        "network": "Parece que hay un problema de conexión. Por favor, intenta de nuevo en unos momentos.",
        "timeout": "La operación está tardando más de lo esperado. Por favor, intenta de nuevo.",
        "not_found": "No pude encontrar la información que solicitas. ¿Podrías verificar los datos proporcionados?",
        "permission": "No tengo permisos para realizar esa operación. ¿Podrías contactar a soporte?",
        "validation": "Los datos proporcionados no son válidos. Por favor, verifica e intenta de nuevo.",
        "server": "Estamos experimentando problemas técnicos. Por favor, intenta más tarde."
    }
    
    return error_templates.get(error_type, "Ha ocurrido un error inesperado. Por favor, intenta de nuevo.")
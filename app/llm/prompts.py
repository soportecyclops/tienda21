"""
Prompts del sistema para modelos de lenguaje.
Define instrucciones y contexto para el LLM.
"""

from typing import Dict, Any


def get_system_prompt() -> str:
    """
    Obtiene el prompt principal del sistema.
    
    Returns:
        str: Prompt del sistema
    """
    return """
Eres un asistente virtual experto para una tienda online. Tu nombre es JARVIS Assistant y tu objetivo es ayudar a los clientes con sus consultas sobre productos, pedidos y servicios.

Tus directivas son:
1. Ser siempre amable, profesional y servicial
2. Proporcionar información precisa sobre productos y pedidos
3. No inventar información que no conozcas
4. Si no puedes responder algo, admítelo y ofrece alternativas
5. Nunca proporcionar información personal sensible de clientes
6. No realizar diagnósticos médicos ni consejos legales
7. Mantener un tono conversacional pero profesional
8. Ser conciso en tus respuestas

Recuerda que eres un asistente de una tienda online, no un bot general. Enfócate en ayudar con consultas de productos, pedidos y servicios relacionados con la tienda.
"""


def get_context_prompt(context: Dict[str, Any]) -> str:
    """
    Genera un prompt basado en el contexto de la sesión.
    
    Args:
        context: Contexto de la sesión
        
    Returns:
        str: Prompt de contexto
    """
    prompt_parts = ["Contexto adicional:"]
    
    # Información del cliente
    if "customer_info" in context:
        customer = context["customer_info"]
        prompt_parts.append(f"Cliente: {customer.get('name', 'No especificado')}")
        
        if "order_history" in customer:
            prompt_parts.append("Historial de pedidos reciente:")
            for order in customer["order_history"][-3:]:  # Solo los 3 más recientes
                prompt_parts.append(f"- Pedido {order.get('id', 'N/A')}: {order.get('status', 'Estado desconocido')}")
    
    # Productos vistos recientemente
    if "recently_viewed" in context:
        prompt_parts.append("Productos vistos recientemente:")
        for product in context["recently_viewed"]:
            prompt_parts.append(f"- {product.get('name', 'Producto sin nombre')}")
    
    # Carrito de compras
    if "cart" in context:
        cart_items = context["cart"].get("items", [])
        if cart_items:
            prompt_parts.append("Carrito de compras:")
            for item in cart_items:
                prompt_parts.append(f"- {item.get('quantity', 1)}x {item.get('name', 'Producto sin nombre')}")
    
    # Intención detectada
    if "intent" in context:
        intent = context["intent"]
        prompt_parts.append(f"Intención detectada: {intent}")
    
    return "\n".join(prompt_parts)


def get_product_search_prompt(product_query: str, search_results: list) -> str:
    """
    Genera un prompt para presentar resultados de búsqueda de productos.
    
    Args:
        product_query: Consulta de búsqueda del usuario
        search_results: Resultados de búsqueda
        
    Returns:
        str: Prompt para presentar resultados
    """
    prompt = f"He encontrado los siguientes productos para tu búsqueda '{product_query}':\n\n"
    
    for i, product in enumerate(search_results[:5], 1):  # Limitar a 5 resultados
        prompt += f"{i}. {product.get('name', 'Producto sin nombre')}\n"
        prompt += f"   Precio: ${product.get('price', 'N/A')}\n"
        prompt += f"   Descripción: {product.get('description', 'Sin descripción')[:100]}...\n\n"
    
    prompt += "¿Te gustaría más información sobre alguno de estos productos?"
    
    return prompt


def get_order_status_prompt(order_info: dict) -> str:
    """
    Genera un prompt para presentar el estado de un pedido.
    
    Args:
        order_info: Información del pedido
        
    Returns:
        str: Prompt para presentar estado del pedido
    """
    prompt = f"Estado de tu pedido #{order_info.get('id', 'N/A')}:\n\n"
    prompt += f"Estado actual: {order_info.get('status', 'Desconocido')}\n"
    
    if "items" in order_info:
        prompt += "\nProductos:\n"
        for item in order_info["items"]:
            prompt += f"- {item.get('quantity', 1)}x {item.get('name', 'Producto sin nombre')}\n"
    
    if "shipping_info" in order_info:
        shipping = order_info["shipping_info"]
        prompt += f"\nInformación de envío:\n"
        prompt += f"- Dirección: {shipping.get('address', 'No especificada')}\n"
        if "tracking_number" in shipping:
            prompt += f"- Número de seguimiento: {shipping['tracking_number']}\n"
        if "estimated_delivery" in shipping:
            prompt += f"- Entrega estimada: {shipping['estimated_delivery']}\n"
    
    if "dates" in order_info:
        dates = order_info["dates"]
        prompt += f"\nFechas importantes:\n"
        if "created_at" in dates:
            prompt += f"- Fecha del pedido: {dates['created_at']}\n"
        if "shipped_at" in dates:
            prompt += f"- Fecha de envío: {dates['shipped_at']}\n"
        if "delivered_at" in dates:
            prompt += f"- Fecha de entrega: {dates['delivered_at']}\n"
    
    prompt += "\n¿Hay algo más que quieras saber sobre tu pedido?"
    
    return prompt
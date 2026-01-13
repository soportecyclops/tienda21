"""
Generador de respuestas finales.
Implementa ensamblaje y formateo de respuestas del bot.
"""

from typing import Dict, List, Optional, Any
import logging

from app.session.models import Session
from app.responses.templates import get_template, get_product_template, get_order_template
from app.observability.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


class ResponseGenerator:
    """Genera respuestas finales para el usuario."""
    
    def __init__(self):
        self.max_response_length = settings.MAX_RESPONSE_LENGTH
    
    async def generate(
        self,
        llm_response: str,
        session: Session
    ) -> str:
        """
        Genera una respuesta final basada en la respuesta del LLM y el contexto.
        
        Args:
            llm_response: Respuesta generada por el LLM
            session: Sesión actual del usuario
            
        Returns:
            str: Respuesta final formateada
        """
        try:
            # Verificar si la respuesta contiene comandos especiales
            processed_response = self._process_special_commands(llm_response, session)
            
            # Verificar longitud de la respuesta
            if len(processed_response) > self.max_response_length:
                processed_response = self._truncate_response(processed_response)
            
            # Formatear respuesta final
            final_response = self._format_response(processed_response, session)
            
            return final_response
        
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return "Lo siento, tuve un problema al procesar tu respuesta. ¿Podrías intentarlo de nuevo?"
    
    def _process_special_commands(
        self,
        response: str,
        session: Session
    ) -> str:
        """
        Procesa comandos especiales en la respuesta del LLM.
        
        Args:
            response: Respuesta del LLM
            session: Sesión actual
            
        Returns:
            str: Respuesta procesada
        """
        # Comandos para mostrar productos
        if "[SHOW_PRODUCT:" in response:
            return self._process_product_command(response, session)
        
        # Comandos para mostrar estado de pedido
        if "[SHOW_ORDER:" in response:
            return self._process_order_command(response, session)
        
        # Comandos para mostrar categorías
        if "[SHOW_CATEGORIES]" in response:
            return self._process_categories_command(response, session)
        
        # Comandos para ofrecer ayuda
        if "[OFFER_HELP]" in response:
            return self._process_help_command(response, session)
        
        return response
    
    def _process_product_command(
        self,
        response: str,
        session: Session
    ) -> str:
        """
        Procesa comandos para mostrar productos.
        
        Args:
            response: Respuesta del LLM
            session: Sesión actual
            
        Returns:
            str: Respuesta procesada con formato de producto
        """
        # Extraer ID del producto
        import re
        match = re.search(r'\[SHOW_PRODUCT:([^\]]+)\]', response)
        if not match:
            return response
        
        product_id = match.group(1)
        
        # Obtener detalles del producto
        # En una implementación real, esto consultaría la base de datos
        product = {
            "id": product_id,
            "name": f"Producto {product_id}",
            "price": 99.99,
            "description": "Descripción del producto",
            "image_url": "https://example.com/image.jpg",
            "stock": 10
        }
        
        # Obtener plantilla de producto
        product_template = get_product_template()
        
        # Formatear plantilla con datos del producto
        formatted_product = product_template.format(
            name=product["name"],
            price=product["price"],
            description=product["description"],
            stock=product["stock"]
        )
        
        # Reemplazar comando con producto formateado
        response = response.replace(f"[SHOW_PRODUCT:{product_id}]", formatted_product)
        
        return response
    
    def _process_order_command(
        self,
        response: str,
        session: Session
    ) -> str:
        """
        Procesa comandos para mostrar estado de pedido.
        
        Args:
            response: Respuesta del LLM
            session: Sesión actual
            
        Returns:
            str: Respuesta procesada con formato de pedido
        """
        # Extraer ID del pedido
        import re
        match = re.search(r'\[SHOW_ORDER:([^\]]+)\]', response)
        if not match:
            return response
        
        order_id = match.group(1)
        
        # Obtener detalles del pedido
        # En una implementación real, esto consultaría la base de datos
        order = {
            "id": order_id,
            "status": "En camino",
            "items": [
                {"name": "Producto 1", "quantity": 2},
                {"name": "Producto 2", "quantity": 1}
            ],
            "total": 199.98,
            "estimated_delivery": "2023-12-15"
        }
        
        # Obtener plantilla de pedido
        order_template = get_order_template()
        
        # Formatear items del pedido
        items_str = ""
        for item in order["items"]:
            items_str += f"- {item['quantity']}x {item['name']}\n"
        
        # Formatear plantilla con datos del pedido
        formatted_order = order_template.format(
            id=order["id"],
            status=order["status"],
            items=items_str,
            total=order["total"],
            estimated_delivery=order["estimated_delivery"]
        )
        
        # Reemplazar comando con pedido formateado
        response = response.replace(f"[SHOW_ORDER:{order_id}]", formatted_order)
        
        return response
    
    def _process_categories_command(
        self,
        response: str,
        session: Session
    ) -> str:
        """
        Procesa comandos para mostrar categorías.
        
        Args:
            response: Respuesta del LLM
            session: Sesión actual
            
        Returns:
            str: Respuesta procesada con lista de categorías
        """
        # Obtener categorías
        # En una implementación real, esto consultaría la base de datos
        categories = [
            "Electrónica",
            "Ropa",
            "Hogar",
            "Deportes",
            "Libros"
        ]
        
        # Formatear lista de categorías
        categories_str = "\n".join([f"- {category}" for category in categories])
        
        # Reemplazar comando con lista de categorías
        response = response.replace("[SHOW_CATEGORIES]", f"Nuestras categorías:\n{categories_str}")
        
        return response
    
    def _process_help_command(
        self,
        response: str,
        session: Session
    ) -> str:
        """
        Procesa comandos para ofrecer ayuda.
        
        Args:
            response: Respuesta del LLM
            session: Sesión actual
            
        Returns:
            str: Respuesta procesada con opciones de ayuda
        """
        # Opciones de ayuda
        help_options = """
Puedo ayudarte con:
- Buscar productos
- Consultar el estado de tu pedido
- Recomendaciones basadas en tus intereses
- Información sobre productos específicos
- Políticas de devolución y garantía

¿Qué necesitas?
        """
        
        # Reemplazar comando con opciones de ayuda
        response = response.replace("[OFFER_HELP]", help_options.strip())
        
        return response
    
    def _truncate_response(self, response: str) -> str:
        """
        Trunca una respuesta si excede la longitud máxima.
        
        Args:
            response: Respuesta a truncar
            
        Returns:
            str: Respuesta truncada
        """
        # Buscar el último punto o salto de línea antes del límite
        truncated = response[:self.max_response_length]
        
        # Intentar cortar en un punto o salto de línea
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        
        cut_pos = max(last_period, last_newline)
        
        if cut_pos > self.max_response_length * 0.8:  # Solo cortar si no perdemos demasiado contenido
            return truncated[:cut_pos + 1] + "\n\n(Respuesta truncada por longitud. ¿Hay algo específico que quieras saber?)"
        else:
            return truncated + "\n\n(Respuesta truncada por longitud. ¿Hay algo específico que quieras saber?)"
    
    def _format_response(
        self,
        response: str,
        session: Session
    ) -> str:
        """
        Formatea la respuesta final.
        
        Args:
            response: Respuesta a formatear
            session: Sesión actual
            
        Returns:
            str: Respuesta formateada
        """
        # Eliminar espacios en blanco múltiples
        import re
        response = re.sub(r'\n\s*\n', '\n\n', response)
        
        # Asegurar que la respuesta termine con puntuación
        if response and response[-1] not in '.!?':
            response += '.'
        
        return response.strip()
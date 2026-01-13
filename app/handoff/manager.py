"""
Gestor de escalamiento a humano.
Implementa lógica para determinar cuándo y cómo escalar a un operador.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.session.models import Session, SessionState
from app.handoff.notifier import Notifier
from app.observability.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


class HandoffManager:
    """Gestiona el escalamiento de conversaciones a operadores humanos."""
    
    def __init__(self):
        self.notifier = Notifier()
    
    async def should_handoff(
        self,
        session: Session,
        last_message: str,
        bot_response: str
    ) -> bool:
        """
        Determina si una conversación debe ser escalada a un humano.
        
        Args:
            session: Sesión actual
            last_message: Último mensaje del usuario
            bot_response: Respuesta generada por el bot
            
        Returns:
            bool: True si se debe escalar, False en caso contrario
        """
        # Verificar si el usuario solicita explícitamente hablar con un humano
        if self._user_requests_human(last_message):
            logger.info(f"Usuario {session.user_id} solicitó hablar con un humano")
            return True
        
        # Verificar si hay múltiples intentos fallidos de ayuda
        if self._multiple_failed_attempts(session):
            logger.info(f"Múltiples intentos fallidos para usuario {session.user_id}")
            return True
        
        # Verificar si hay frustración detectada
        if self._frustration_detected(last_message):
            logger.info(f"Frustración detectada para usuario {session.user_id}")
            return True
        
        # Verificar si el tema es complejo y requiere intervención humana
        if self._complex_topic_detected(last_message):
            logger.info(f"Tema complejo detectado para usuario {session.user_id}")
            return True
        
        # Verificar si la conversación es muy larga
        if self._long_conversation(session):
            logger.info(f"Conversación larga detectada para usuario {session.user_id}")
            return True
        
        return False
    
    async def initiate_handoff(
        self,
        session: Session,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Inicia el proceso de escalamiento a un humano.
        
        Args:
            session: Sesión a escalar
            reason: Razón del escalamiento
            context: Contexto adicional
            
        Returns:
            Dict[str, Any]: Resultado del proceso de escalamiento
        """
        try:
            # Actualizar estado de la sesión
            session.state = SessionState.ESCALATED
            
            # Preparar contexto para el operador
            handoff_context = self._prepare_handoff_context(session, reason, context)
            
            # Enviar notificación al operador
            notification_result = await self.notifier.notify_operator(handoff_context)
            
            # Registrar el escalamiento
            logger.info(f"Escalamiento iniciado para sesión {session.session_id}: {reason}")
            
            return {
                "success": True,
                "session_id": session.session_id,
                "reason": reason,
                "notification_sent": notification_result["success"],
                "estimated_wait_time": "5-10 minutos"
            }
        
        except Exception as e:
            logger.error(f"Error iniciando escalamiento: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session.session_id
            }
    
    def _user_requests_human(self, message: str) -> bool:
        """
        Verifica si el usuario solicita explícitamente hablar con un humano.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            bool: True si el usuario solicita un humano, False en caso contrario
        """
        human_request_patterns = [
            "hablar con un humano",
            "quiero hablar con alguien",
            "puedo hablar con un operador",
            "necesito hablar con una persona",
            "humano por favor",
            "operador",
            "agente",
            "persona",
            "alguien real"
        ]
        
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in human_request_patterns)
    
    def _multiple_failed_attempts(self, session: Session) -> bool:
        """
        Verifica si hay múltiples intentos fallidos de ayuda.
        
        Args:
            session: Sesión actual
            
        Returns:
            bool: True si hay múltiples intentos fallidos, False en caso contrario
        """
        # Contar mensajes del usuario en los últimos 10 intercambios
        recent_messages = session.messages[-10:] if len(session.messages) > 10 else session.messages
        user_messages = [msg for msg in recent_messages if msg.role.value == "user"]
        
        # Si hay más de 5 mensajes del usuario, podría indicar frustración
        return len(user_messages) >= 5
    
    def _frustration_detected(self, message: str) -> bool:
        """
        Verifica si hay señales de frustración en el mensaje.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            bool: True si hay frustración, False en caso contrario
        """
        frustration_patterns = [
            "no funciona",
            "no entiendo",
            "no me ayudaste",
            "inútil",
            "frustrante",
            "malo",
            "terrible",
            "no sirve",
            "estoy cansado",
            "no puedo",
            "imposible"
        ]
        
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in frustration_patterns)
    
    def _complex_topic_detected(self, message: str) -> bool:
        """
        Verifica si el mensaje trata sobre un tema complejo que requiere intervención humana.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            bool: True si es un tema complejo, False en caso contrario
        """
        complex_topic_patterns = [
            "reembolso",
            "devolución",
            "queja",
            "problema con el pago",
            "facturación",
            "cancelar pedido",
            "urgente",
            "emergencia",
            "gerente",
            "supervisor"
        ]
        
        message_lower = message.lower()
        return any(pattern in message_lower for pattern in complex_topic_patterns)
    
    def _long_conversation(self, session: Session) -> bool:
        """
        Verifica si la conversación es muy larga.
        
        Args:
            session: Sesión actual
            
        Returns:
            bool: True si la conversación es larga, False en caso contrario
        """
        # Si hay más de 20 mensajes, podría ser una conversación larga
        return len(session.messages) >= 20
    
    def _prepare_handoff_context(
        self,
        session: Session,
        reason: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepara el contexto para el operador humano.
        
        Args:
            session: Sesión a escalar
            reason: Razón del escalamiento
            additional_context: Contexto adicional
            
        Returns:
            Dict[str, Any]: Contexto completo para el operador
        """
        # Extraer mensajes recientes
        recent_messages = session.messages[-10:] if len(session.messages) > 10 else session.messages
        
        # Formatear mensajes para legibilidad
        formatted_messages = []
        for msg in recent_messages:
            formatted_messages.append({
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            })
        
        # Construir contexto completo
        context = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "reason": reason,
            "session_duration": (datetime.now() - session.created_at).total_seconds(),
            "message_count": len(session.messages),
            "recent_messages": formatted_messages,
            "session_context": session.context
        }
        
        # Agregar contexto adicional si se proporciona
        if additional_context:
            context.update(additional_context)
        
        return context
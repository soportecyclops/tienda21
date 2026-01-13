"""
Sistema de notificación para escalamiento a humano.
Implementa envío de notificaciones por email, Slack o webhook.
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import logging

import httpx
from app.observability.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


class Notifier:
    """Gestiona el envío de notificaciones a operadores humanos."""
    
    def __init__(self):
        self.provider = settings.NOTIFICATION_PROVIDER.lower()
    
    async def notify_operator(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notifica a un operador sobre un escalamiento.
        
        Args:
            context: Contexto del escalamiento
            
        Returns:
            Dict[str, Any]: Resultado de la notificación
        """
        try:
            if self.provider == "email":
                return await self._send_email_notification(context)
            elif self.provider == "slack":
                return await self._send_slack_notification(context)
            elif self.provider == "webhook":
                return await self._send_webhook_notification(context)
            else:
                logger.error(f"Proveedor de notificación no reconocido: {self.provider}")
                return {
                    "success": False,
                    "error": f"Proveedor no reconocido: {self.provider}"
                }
        
        except Exception as e:
            logger.error(f"Error enviando notificación: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_email_notification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía una notificación por email.
        
        Args:
            context: Contexto del escalamiento
            
        Returns:
            Dict[str, Any]: Resultado del envío
        """
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
            logger.error("Configuración SMTP incompleta")
            return {
                "success": False,
                "error": "Configuración SMTP incompleta"
            }
        
        try:
            # Preparar mensaje
            subject = f"Escalamiento requerido - Sesión {context['session_id']}"
            
            # Formatear cuerpo del mensaje
            body = self._format_email_body(context)
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_USER
            msg["To"] = settings.SMTP_USER  # Enviar al mismo usuario por simplicidad
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "html"))
            
            # Enviar email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Notificación por email enviada para sesión {context['session_id']}")
            
            return {
                "success": True,
                "provider": "email",
                "message_id": context['session_id']
            }
        
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_slack_notification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía una notificación a Slack.
        
        Args:
            context: Contexto del escalamiento
            
        Returns:
            Dict[str, Any]: Resultado del envío
        """
        if not settings.SLACK_WEBHOOK_URL:
            logger.error("URL de webhook de Slack no configurada")
            return {
                "success": False,
                "error": "URL de webhook de Slack no configurada"
            }
        
        try:
            # Preparar payload para Slack
            payload = {
                "text": f"Escalamiento requerido - Sesión {context['session_id']}",
                "attachments": [
                    {
                        "color": "warning",
                        "fields": [
                            {
                                "title": "ID de Sesión",
                                "value": context['session_id'],
                                "short": True
                            },
                            {
                                "title": "ID de Usuario",
                                "value": context['user_id'],
                                "short": True
                            },
                            {
                                "title": "Razón",
                                "value": context['reason'],
                                "short": False
                            },
                            {
                                "title": "Duración de Sesión",
                                "value": f"{context['session_duration']:.0f} segundos",
                                "short": True
                            },
                            {
                                "title": "Cantidad de Mensajes",
                                "value": str(context['message_count']),
                                "short": True
                            }
                        ],
                        "footer": "JARVIS Commercial Bot",
                        "ts": datetime.now().timestamp()
                    }
                ]
            }
            
            # Enviar a Slack
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    settings.SLACK_WEBHOOK_URL,
                    json=payload
                )
                response.raise_for_status()
            
            logger.info(f"Notificación de Slack enviada para sesión {context['session_id']}")
            
            return {
                "success": True,
                "provider": "slack",
                "message_id": context['session_id']
            }
        
        except Exception as e:
            logger.error(f"Error enviando notificación de Slack: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_webhook_notification(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía una notificación a través de un webhook genérico.
        
        Args:
            context: Contexto del escalamiento
            
        Returns:
            Dict[str, Any]: Resultado del envío
        """
        if not settings.HANDOFF_WEBHOOK_URL:
            logger.error("URL de webhook de escalamiento no configurada")
            return {
                "success": False,
                "error": "URL de webhook de escalamiento no configurada"
            }
        
        try:
            # Preparar payload
            payload = {
                "event": "handoff_required",
                "timestamp": datetime.now().isoformat(),
                "data": context
            }
            
            # Enviar webhook
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    settings.HANDOFF_WEBHOOK_URL,
                    json=payload
                )
                response.raise_for_status()
            
            logger.info(f"Notificación de webhook enviada para sesión {context['session_id']}")
            
            return {
                "success": True,
                "provider": "webhook",
                "message_id": context['session_id']
            }
        
        except Exception as e:
            logger.error(f"Error enviando notificación de webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _format_email_body(self, context: Dict[str, Any]) -> str:
        """
        Formatea el cuerpo del email.
        
        Args:
            context: Contexto del escalamiento
            
        Returns:
            str: Cuerpo del email formateado en HTML
        """
        # Formatear mensajes recientes
        recent_messages = ""
        for msg in context["recent_messages"]:
            role_color = "blue" if msg["role"] == "user" else "green"
            recent_messages += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">
                    <span style="color: {role_color}; font-weight: bold;">{msg["role"].title()}:</span>
                    {msg["content"]}
                </td>
            </tr>
            """
        
        # Construir HTML
        html = f"""
        <html>
        <body>
            <h2>Escalamiento Requerido</h2>
            
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">ID de Sesión:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{context["session_id"]}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">ID de Usuario:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{context["user_id"]}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Razón:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{context["reason"]}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Duración de Sesión:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{context["session_duration"]:.0f} segundos</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Cantidad de Mensajes:</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{context["message_count"]}</td>
                </tr>
            </table>
            
            <h3>Mensajes Recientes:</h3>
            <table style="border-collapse: collapse; width: 100%;">
                {recent_messages}
            </table>
            
            <p>Por favor, inicia sesión en el panel de control para atender esta solicitud.</p>
        </body>
        </html>
        """
        
        return html


# Importar datetime aquí para evitar dependencias circulares
from datetime import datetime
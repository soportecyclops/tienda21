"""
Capa de abstracción para modelos de lenguaje (LLM).
Implementa interfaz unificada para múltiples proveedores.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

from app.llm.providers import MistralProvider, GroqProvider, OpenAIProvider
from app.llm.prompts import get_system_prompt, get_context_prompt
from app.session.models import Session
from app.config import settings
from app.observability.logger import get_logger

logger = get_logger(__name__)


class LLMProvider(ABC):
    """Clase base abstracta para proveedores de LLM."""
    
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Genera una respuesta basada en los mensajes proporcionados."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Verifica si el proveedor está disponible."""
        pass


class LLMAdapter:
    """Adaptador para interactuar con diferentes proveedores de LLM."""
    
    def __init__(self):
        self.provider_name = settings.LLM_PROVIDER.lower()
        self.provider = self._get_provider()
        self.fallback_providers = self._get_fallback_providers()
    
    async def process_message(
        self,
        message: str,
        session: Session
    ) -> str:
        """
        Procesa un mensaje utilizando el LLM configurado.
        
        Args:
            message: Mensaje del usuario
            session: Sesión actual del usuario
            
        Returns:
            str: Respuesta generada por el LLM
        """
        # Construir mensajes para el LLM
        messages = self._build_messages(message, session)
        
        # Intentar generar respuesta con el proveedor principal
        try:
            response = await self._generate_with_provider(
                self.provider,
                messages
            )
            logger.info(f"Respuesta generada con {self.provider_name}")
            return response
        except Exception as e:
            logger.error(f"Error con proveedor principal {self.provider_name}: {str(e)}")
            
            # Intentar con proveedores de fallback
            for fallback_provider in self.fallback_providers:
                try:
                    response = await self._generate_with_provider(
                        fallback_provider,
                        messages
                    )
                    provider_name = type(fallback_provider).__name__.replace("Provider", "").lower()
                    logger.info(f"Respuesta generada con fallback {provider_name}")
                    return response
                except Exception as fallback_error:
                    logger.error(f"Error con fallback {type(fallback_provider).__name__}: {str(fallback_error)}")
            
            # Si todos los proveedores fallan, retornar respuesta por defecto
            logger.error("Todos los proveedores LLM fallaron")
            return "Lo siento, estoy experimentando dificultades técnicas. Por favor, intenta más tarde."
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Verifica el estado de salud de todos los proveedores.
        
        Returns:
            Dict[str, bool]: Estado de cada proveedor
        """
        results = {}
        
        # Verificar proveedor principal
        try:
            results[self.provider_name] = await self.provider.health_check()
        except Exception as e:
            logger.error(f"Error verificando proveedor principal: {str(e)}")
            results[self.provider_name] = False
        
        # Verificar proveedores de fallback
        for provider in self.fallback_providers:
            provider_name = type(provider).__name__.replace("Provider", "").lower()
            try:
                results[provider_name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Error verificando fallback {provider_name}: {str(e)}")
                results[provider_name] = False
        
        return results
    
    def _get_provider(self) -> LLMProvider:
        """Obtiene el proveedor principal configurado."""
        if self.provider_name == "mistral":
            return MistralProvider(api_key=settings.MISTRAL_API_KEY)
        elif self.provider_name == "groq":
            return GroqProvider(api_key=settings.GROQ_API_KEY)
        elif self.provider_name == "openai":
            return OpenAIProvider(api_key=settings.OPENAI_API_KEY)
        else:
            logger.error(f"Proveedor LLM no reconocido: {self.provider_name}")
            raise ValueError(f"Proveedor LLM no reconocido: {self.provider_name}")
    
    def _get_fallback_providers(self) -> List[LLMProvider]:
        """Obtiene la lista de proveedores de fallback."""
        fallback_providers = []
        
        # Definir orden de fallback
        fallback_order = ["mistral", "groq", "openai"]
        
        # Excluir el proveedor principal
        if self.provider_name in fallback_order:
            fallback_order.remove(self.provider_name)
        
        # Crear instancias de proveedores de fallback
        for provider_name in fallback_order:
            try:
                if provider_name == "mistral" and settings.MISTRAL_API_KEY:
                    fallback_providers.append(MistralProvider(api_key=settings.MISTRAL_API_KEY))
                elif provider_name == "groq" and settings.GROQ_API_KEY:
                    fallback_providers.append(GroqProvider(api_key=settings.GROQ_API_KEY))
                elif provider_name == "openai" and settings.OPENAI_API_KEY:
                    fallback_providers.append(OpenAIProvider(api_key=settings.OPENAI_API_KEY))
            except Exception as e:
                logger.warning(f"No se pudo inicializar fallback {provider_name}: {str(e)}")
        
        return fallback_providers
    
    def _build_messages(
        self,
        message: str,
        session: Session
    ) -> List[Dict[str, str]]:
        """
        Construye la lista de mensajes para enviar al LLM.
        
        Args:
            message: Mensaje actual del usuario
            session: Sesión actual
            
        Returns:
            List[Dict[str, str]]: Lista de mensajes formateados
        """
        messages = []
        
        # Agregar prompt del sistema
        system_prompt = get_system_prompt()
        messages.append({"role": "system", "content": system_prompt})
        
        # Agregar contexto si está disponible
        if session.context:
            context_prompt = get_context_prompt(session.context)
            messages.append({"role": "system", "content": context_prompt})
        
        # Agregar historial de mensajes (limitado a los últimos 10)
        recent_messages = session.messages[-10:] if len(session.messages) > 10 else session.messages
        
        for msg in recent_messages:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Agregar mensaje actual
        messages.append({"role": "user", "content": message})
        
        return messages
    
    async def _generate_with_provider(
        self,
        provider: LLMProvider,
        messages: List[Dict[str, str]]
    ) -> str:
        """
        Genera una respuesta con un proveedor específico.
        
        Args:
            provider: Proveedor a utilizar
            messages: Mensajes para enviar
            
        Returns:
            str: Respuesta generada
        """
        try:
            response = await provider.generate_response(
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            raise
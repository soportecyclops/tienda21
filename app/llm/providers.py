"""
Implementaciones de proveedores de LLM.
Define conectores para Mistral, Groq, OpenAI y otros.
"""

import json
import httpx
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

from app.observability.logger import get_logger

logger = get_logger(__name__)


class MistralProvider:
    """Proveedor para el modelo Mistral AI."""
    
    def __init__(self, api_key: str, model: str = "mistral-medium"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.mistral.ai/v1"
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Genera una respuesta usando Mistral AI."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP en Mistral: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error en Mistral: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Verifica si el servicio Mistral está disponible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error en health check de Mistral: {str(e)}")
            return False


class GroqProvider:
    """Proveedor para el modelo Groq."""
    
    def __init__(self, api_key: str, model: str = "llama2-70b-4096"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Genera una respuesta usando Groq."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP en Groq: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error en Groq: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Verifica si el servicio Groq está disponible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error en health check de Groq: {str(e)}")
            return False


class OpenAIProvider:
    """Proveedor para modelos OpenAI."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """Genera una respuesta usando OpenAI."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP en OpenAI: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error en OpenAI: {str(e)}")
            raise
    
    async def health_check(self) -> bool:
        """Verifica si el servicio OpenAI está disponible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error en health check de OpenAI: {str(e)}")
            return False
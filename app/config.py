"""
Configuración centralizada del bot comercial JARVIS.
Define variables de entorno, flags y settings.

Este archivo es infraestructura.
No contiene lógica de negocio.
"""

from typing import List, Optional
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración principal de la aplicación."""

    # =========================
    # Configuración del servidor
    # =========================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # =========================
    # Configuración de CORS
    # =========================
    ALLOWED_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # =========================
    # Configuración de base de datos
    # =========================
    DATABASE_URL: str = "sqlite:///./data/bot.db"

    # =========================
    # Configuración de LLM
    # =========================
    LLM_PROVIDER: str = "mistral"  # mistral, groq, openai
    MISTRAL_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # =========================
    # Configuración de Tienda Nube
    # =========================
    TIENDANUBE_API_KEY: Optional[str] = None
    TIENDANUBE_STORE_ID: Optional[str] = None
    TIENDANUBE_WEBHOOK_SECRET: Optional[str] = None

    # =========================
    # Configuración de notificaciones
    # =========================
    NOTIFICATION_PROVIDER: str = "email"  # email, slack, webhook
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    HANDOFF_WEBHOOK_URL: Optional[str] = None

    # =========================
    # Configuración de sesión
    # =========================
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_SESSIONS: int = 1000

    # =========================
    # Configuración de reglas
    # =========================
    RULES_STRICT_MODE: bool = True
    MAX_RESPONSE_LENGTH: int = 500

    # =========================
    # Validadores
    # =========================
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # =========================
    # Configuración Pydantic v2
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Retorna una instancia singleton de Settings.
    Evita recargas múltiples de configuración.
    """
    return Settings()


# Alias canónico usado por el resto del sistema
settings = get_settings()

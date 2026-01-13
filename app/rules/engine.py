"""
Archivo: app/rules/engine.py

Utilidad:
---------
Motor de reglas y guardrails para validación de mensajes y respuestas.
Define límites cognitivos, seguridad y control de abuso.
"""

import re
from typing import Optional
from datetime import datetime

from app.rules.patterns import get_patterns, get_forbidden_patterns
from app.session.models import Session
from app.observability.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


class RuleResult:
    def __init__(
        self,
        is_violation: bool,
        rule_name: str,
        response: Optional[str] = None,
        confidence: float = 0.0,
    ):
        self.is_violation = is_violation
        self.rule_name = rule_name
        self.response = response
        self.confidence = confidence


class RulesEngine:
    """
    Motor de evaluación de reglas para mensajes entrantes y salientes.
    """

    def __init__(self):
        self.strict_mode = settings.RULES_STRICT_MODE
        self.max_response_length = settings.MAX_RESPONSE_LENGTH

        self.patterns = get_patterns()
        self.forbidden_patterns = get_forbidden_patterns()

        # Patrones de inyección de prompt (EN + ES)
        self.prompt_injection_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in [
                r"ignore.*instructions",
                r"forget.*previous",
                r"system.*prompt",
                r"act.*as.*different",
                r"roleplay.*as",
                r"ignora.*instrucciones",
                r"olvida.*instrucciones",
                r"actúa.*como",
                r"comportate.*como",
            ]
        ]

        # Contenido sensible en respuestas
        self.sensitive_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in [
                r"password",
                r"secret.*key",
                r"token",
                r"api.*key",
                r"credential",
            ]
        ]

    # ------------------------------------------------------------------
    # MENSAJES DE USUARIO
    # ------------------------------------------------------------------

    async def check_message(self, message: str, session: Session) -> RuleResult:
        normalized = message.lower().strip()

        # 1. Patrones prohibidos explícitos
        for name, pattern in self.forbidden_patterns.items():
            if pattern.search(normalized):
                logger.warning(f"[RULE] Forbidden pattern detectado: {name}")
                return RuleResult(
                    True,
                    f"forbidden_pattern_{name}",
                    "No puedo procesar ese tipo de solicitud.",
                    0.95,
                )

        # 2. Longitud excesiva
        if len(message) > 1000:
            return RuleResult(
                True,
                "message_too_long",
                "Tu mensaje es demasiado largo.",
                1.0,
            )

        # 3. Repetición exacta del último mensaje
        if session.messages:
            last_user_messages = [
                m for m in reversed(session.messages) if m.role == "user"
            ]
            if last_user_messages:
                last = last_user_messages[0]
                if last.content.lower().strip() == normalized:
                    return RuleResult(
                        True,
                        "repeated_message",
                        "Parece que ya enviaste ese mensaje.",
                        0.8,
                    )

        # 4. Spam por frecuencia (3 mensajes < 60s)
        recent = [
            m
            for m in session.messages
            if m.role == "user"
            and (datetime.now() - m.timestamp).total_seconds() < 60
        ]

        if len(recent) >= 3:
            return RuleResult(
                True,
                "spam_detected",
                "Estás enviando mensajes muy rápido.",
                0.75,
            )

        # 5. Inyección de prompt
        for pattern in self.prompt_injection_patterns:
            if pattern.search(normalized):
                logger.warning("[RULE] Intento de prompt injection detectado")
                return RuleResult(
                    True,
                    "prompt_injection",
                    "No puedo cambiar mis instrucciones.",
                    0.85,
                )

        return RuleResult(False, "all_rules_passed", confidence=1.0)

    # ------------------------------------------------------------------
    # RESPUESTAS DEL SISTEMA
    # ------------------------------------------------------------------

    async def check_response(self, response: str, session: Session) -> RuleResult:
        if len(response) > self.max_response_length:
            return RuleResult(
                True,
                "response_too_long",
                "Mi respuesta es demasiado larga.",
                1.0,
            )

        for pattern in self.sensitive_patterns:
            if pattern.search(response):
                return RuleResult(
                    True,
                    "sensitive_content",
                    "No puedo proporcionar esa información.",
                    0.9,
                )

        return RuleResult(False, "response_valid", confidence=1.0)

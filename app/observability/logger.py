"""
Sistema de logging estructurado.
Implementa configuración y utilidades para logging.
"""

import logging
import sys
from typing import Optional, Dict, Any
import json
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Formateador para logs estructurados en JSON."""
    
    def format(self, record):
        """Formatea un registro de log como JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Agregar información adicional si está disponible
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, "session_id"):
            log_entry["session_id"] = record.session_id
        
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        # Agregar información de excepción si hay un error
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


def setup_logging(
    level: str = "INFO",
    structured: bool = True,
    file_path: Optional[str] = None
) -> None:
    """
    Configura el sistema de logging.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: Si se deben usar logs estructurados (JSON)
        file_path: Ruta al archivo de log (opcional)
    """
    # Configurar nivel de logging
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Crear formateador
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Configurar handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configurar handlers
    handlers = [console_handler]
    
    # Agregar handler de archivo si se especifica
    if file_path:
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configurar logger raíz
    logging.basicConfig(
        level=log_level,
        handlers=handlers
    )
    
    # Configurar loggers específicos
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.
    
    Args:
        name: Nombre del logger
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Registra un mensaje con contexto adicional.
    
    Args:
        logger: Logger a utilizar
        level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Mensaje a registrar
        context: Contexto adicional
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if context:
        # Crear un registro de log con contexto adicional
        record = logger.makeRecord(
            name=logger.name,
            level=log_level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        
        # Agregar contexto al registro
        for key, value in context.items():
            setattr(record, key, value)
        
        logger.handle(record)
    else:
        logger.log(log_level, message)
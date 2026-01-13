"""
Utilidades de tiempo.
Implementa funciones para manejo de fechas y horas.
"""

from datetime import datetime, timedelta
from typing import Optional, Union
import time


def now_iso() -> str:
    """
    Obtiene la fecha y hora actual en formato ISO.
    
    Returns:
        str: Fecha y hora actual en formato ISO
    """
    return datetime.utcnow().isoformat()


def iso_to_datetime(iso_string: str) -> datetime:
    """
    Convierte una cadena ISO a datetime.
    
    Args:
        iso_string: Cadena en formato ISO
        
    Returns:
        datetime: Objeto datetime
    """
    return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))


def format_duration(seconds: float) -> str:
    """
    Formatea una duración en segundos a una cadena legible.
    
    Args:
        seconds: Duración en segundos
        
    Returns:
        str: Duración formateada
    """
    if seconds < 60:
        return f"{seconds:.1f} segundos"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutos"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} horas"


def time_ago(dt: datetime) -> str:
    """
    Calcula cuánto tiempo ha pasado desde una fecha.
    
    Args:
        dt: Fecha de referencia
        
    Returns:
        str: Tiempo transcurrido formateado
    """
    now = datetime.utcnow()
    delta = now - dt
    
    if delta.days > 0:
        return f"hace {delta.days} día{'s' if delta.days > 1 else ''}"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"hace {hours} hora{'s' if hours > 1 else ''}"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
    else:
        return f"hace {delta.seconds} segundo{'s' if delta.seconds != 1 else ''}"


def add_business_days(start_date: datetime, days: int) -> datetime:
    """
    Agrega días hábiles a una fecha.
    
    Args:
        start_date: Fecha de inicio
        days: Número de días hábiles a agregar
        
    Returns:
        datetime: Fecha resultante
    """
    current_date = start_date
    added_days = 0
    
    while added_days < days:
        current_date += timedelta(days=1)
        
        # Si es día de semana (lunes a viernes)
        if current_date.weekday() < 5:
            added_days += 1
    
    return current_date


def parse_time_string(time_str: str) -> Optional[datetime]:
    """
    Intenta parsear una cadena de tiempo en varios formatos comunes.
    
    Args:
        time_str: Cadena de tiempo
        
    Returns:
        Optional[datetime]: Objeto datetime o None si no se pudo parsear
    """
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M:%S"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    
    return None


def get_timestamp() -> int:
    """
    Obtiene el timestamp actual en segundos.
    
    Returns:
        int: Timestamp actual
    """
    return int(time.time())


def get_timestamp_ms() -> int:
    """
    Obtiene el timestamp actual en milisegundos.
    
    Returns:
        int: Timestamp actual en milisegundos
    """
    return int(time.time() * 1000)


def sleep(seconds: Union[int, float]) -> None:
    """
    Duerme el hilo actual por la cantidad de segundos especificada.
    
    Args:
        seconds: Segundos a dormir
    """
    time.sleep(seconds)
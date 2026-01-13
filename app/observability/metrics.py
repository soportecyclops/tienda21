"""
Sistema de métricas y KPIs.
Implementa registro y seguimiento de métricas operativas.
"""

import time
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque
import threading
import logging

from app.observability.logger import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Colector de métricas para el bot comercial."""
    
    def __init__(self):
        self._metrics = defaultdict(float)
        self._counters = defaultdict(int)
        self._timers = defaultdict(list)
        self._lock = threading.Lock()
    
    def increment(self, metric_name: str, value: float = 1.0) -> None:
        """
        Incrementa una métrica.
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor a incrementar (por defecto 1.0)
        """
        with self._lock:
            self._metrics[metric_name] += value
            self._counters[metric_name] += 1
    
    def set(self, metric_name: str, value: float) -> None:
        """
        Establece el valor de una métrica.
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor a establecer
        """
        with self._lock:
            self._metrics[metric_name] = value
    
    def timer(self, metric_name: str) -> "Timer":
        """
        Crea un temporizador para una métrica.
        
        Args:
            metric_name: Nombre de la métrica
            
        Returns:
            Timer: Temporizador contextual
        """
        return Timer(self, metric_name)
    
    def record_time(self, metric_name: str, duration: float) -> None:
        """
        Registra un tiempo para una métrica.
        
        Args:
            metric_name: Nombre de la métrica
            duration: Duración en segundos
        """
        with self._lock:
            self._timers[metric_name].append(duration)
            
            # Mantener solo los últimos 1000 valores
            if len(self._timers[metric_name]) > 1000:
                self._timers[metric_name] = self._timers[metric_name][-1000:]
    
    def get_metric(self, metric_name: str) -> Optional[float]:
        """
        Obtiene el valor de una métrica.
        
        Args:
            metric_name: Nombre de la métrica
            
        Returns:
            Optional[float]: Valor de la métrica o None si no existe
        """
        with self._lock:
            return self._metrics.get(metric_name)
    
    def get_counter(self, metric_name: str) -> int:
        """
        Obtiene el contador de una métrica.
        
        Args:
            metric_name: Nombre de la métrica
            
        Returns:
            int: Valor del contador
        """
        with self._lock:
            return self._counters.get(metric_name, 0)
    
    def get_timer_stats(self, metric_name: str) -> Dict[str, float]:
        """
        Obtiene estadísticas de tiempo para una métrica.
        
        Args:
            metric_name: Nombre de la métrica
            
        Returns:
            Dict[str, float]: Estadísticas (count, avg, min, max, p50, p95, p99)
        """
        with self._lock:
            times = self._timers.get(metric_name, [])
            
            if not times:
                return {
                    "count": 0,
                    "avg": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "p50": 0.0,
                    "p95": 0.0,
                    "p99": 0.0
                }
            
            times_sorted = sorted(times)
            count = len(times_sorted)
            
            return {
                "count": count,
                "avg": sum(times_sorted) / count,
                "min": times_sorted[0],
                "max": times_sorted[-1],
                "p50": times_sorted[int(count * 0.5)],
                "p95": times_sorted[int(count * 0.95)],
                "p99": times_sorted[int(count * 0.99)]
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Obtiene todas las métricas y estadísticas.
        
        Returns:
            Dict[str, Any]: Todas las métricas y estadísticas
        """
        with self._lock:
            result = {}
            
            # Métricas simples
            for name, value in self._metrics.items():
                result[name] = {
                    "value": value,
                    "count": self._counters.get(name, 0)
                }
            
            # Estadísticas de tiempo
            for name in self._timers:
                result[f"{name}_stats"] = self.get_timer_stats(name)
            
            return result


class Timer:
    """Context manager para medir tiempo de ejecución."""
    
    def __init__(self, collector: MetricsCollector, metric_name: str):
        self.collector = collector
        self.metric_name = metric_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.collector.record_time(self.metric_name, duration)


# Instancia global del colector de métricas
metrics = MetricsCollector()


def setup_metrics() -> None:
    """Configura el sistema de métricas."""
    logger.info("Sistema de métricas configurado")


def track_webhook_received(source: str, event_type: str) -> None:
    """
    Registra la recepción de un webhook.
    
    Args:
        source: Fuente del webhook (tiendanube, chat, etc.)
        event_type: Tipo de evento
    """
    metrics.increment(f"webhooks.{source}.received")
    metrics.increment(f"webhooks.{source}.{event_type}")


def track_message_processed(user_id: str, response_time: float) -> None:
    """
    Registra el procesamiento de un mensaje.
    
    Args:
        user_id: ID del usuario
        response_time: Tiempo de respuesta en segundos
    """
    metrics.increment("messages.processed")
    metrics.record_time("messages.response_time", response_time)


def track_llm_request(provider: str, success: bool, response_time: float) -> None:
    """
    Registra una solicitud al LLM.
    
    Args:
        provider: Proveedor del LLM (mistral, groq, openai)
        success: Si la solicitud fue exitosa
        response_time: Tiempo de respuesta en segundos
    """
    status = "success" if success else "error"
    metrics.increment(f"llm.{provider}.{status}")
    metrics.record_time(f"llm.{provider}.response_time", response_time)


def track_handoff(reason: str) -> None:
    """
    Registra un escalamiento a humano.
    
    Args:
        reason: Razón del escalamiento
    """
    metrics.increment("handoffs.total")
    metrics.increment(f"handoffs.{reason}")


def track_database_operation(operation: str, success: bool, response_time: float) -> None:
    """
    Registra una operación de base de datos.
    
    Args:
        operation: Tipo de operación (read, write, etc.)
        success: Si la operación fue exitosa
        response_time: Tiempo de respuesta en segundos
    """
    status = "success" if success else "error"
    metrics.increment(f"db.{operation}.{status}")
    metrics.record_time(f"db.{operation}.response_time", response_time)
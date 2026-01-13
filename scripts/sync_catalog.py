"""
Script para sincronizar el catálogo de Tienda Nube.
Implementa actualización periódica del catálogo local.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos de la app
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from app.context.loader import CatalogLoader
from app.observability.logger import setup_logging, get_logger
from app.config import settings


async def sync_catalog(force: bool = False) -> None:
    """
    Sincroniza el catálogo de Tienda Nube.
    
    Args:
        force: Si se debe forzar la sincronización completa
    """
    logger = get_logger(__name__)
    
    try:
        # Inicializar base de datos
        from app.context.store import init_db
        await init_db()
        
        # Crear cargador de catálogo
        loader = CatalogLoader()
        
        # Sincronizar catálogo
        logger.info("Iniciando sincronización de catálogo...")
        result = await loader.sync_catalog()
        
        if result["success"]:
            logger.info(f"Sincronización completada: {result['products_count']} productos")
        else:
            logger.error(f"Error en sincronización: {result['error']}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error en sincronización: {str(e)}")
        sys.exit(1)


def main():
    """Función principal del script."""
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Sincronizar catálogo de Tienda Nube")
    parser.add_argument("--force", action="store_true", help="Forzar sincronización completa")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostrar logs detallados")
    
    args = parser.parse_args()
    
    # Configurar logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    
    # Ejecutar sincronización
    asyncio.run(sync_catalog(force=args.force))


if __name__ == "__main__":
    main()
"""
Cargador de catálogo y datos contextuales.
Implementa sincronización con Tienda Nube y carga de datos.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from app.context.store import save_catalog, get_catalog, get_product
from app.observability.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


class CatalogLoader:
    """Gestiona la carga y sincronización del catálogo de productos."""
    
    def __init__(self):
        self.api_key = settings.TIENDANUBE_API_KEY
        self.store_id = settings.TIENDANUBE_STORE_ID
        self.base_url = f"https://api.tiendanube.com/v1/{self.store_id}"
    
    async def sync_catalog(self) -> Dict[str, Any]:
        """
        Sincroniza el catálogo completo desde Tienda Nube.
        
        Returns:
            Dict[str, Any]: Resultado de la sincronización
        """
        if not self.api_key or not self.store_id:
            logger.error("Credenciales de Tienda Nube no configuradas")
            return {
                "success": False,
                "error": "Credenciales no configuradas",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Obtener productos desde la API
            products = await self._fetch_products()
            
            # Guardar catálogo en la base de datos local
            await save_catalog(products)
            
            logger.info(f"Catálogo sincronizado: {len(products)} productos")
            
            return {
                "success": True,
                "products_count": len(products),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error sincronizando catálogo: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles de un producto específico.
        
        Args:
            product_id: ID del producto
            
        Returns:
            Optional[Dict[str, Any]]: Detalles del producto o None si no existe
        """
        # Primero intentar obtener desde la base de datos local
        product = await get_product(product_id)
        if product:
            return product
        
        # Si no está en la base de datos, intentar obtener desde la API
        try:
            product = await self._fetch_product(product_id)
            if product:
                # Guardar en la base de datos para futuras consultas
                await save_catalog([product])
                return product
        except Exception as e:
            logger.error(f"Error obteniendo producto {product_id}: {str(e)}")
        
        return None
    
    async def search_products(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Busca productos por nombre o descripción.
        
        Args:
            query: Término de búsqueda
            limit: Número máximo de resultados
            
        Returns:
            List[Dict[str, Any]]: Lista de productos que coinciden con la búsqueda
        """
        catalog = await get_catalog()
        
        # Búsqueda simple por nombre o descripción
        results = []
        query_lower = query.lower()
        
        for product in catalog:
            if (
                query_lower in product.get("name", "").lower() or
                query_lower in product.get("description", "").lower()
            ):
                results.append(product)
                if len(results) >= limit:
                    break
        
        return results
    
    async def get_featured_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene productos destacados.
        
        Args:
            limit: Número máximo de productos
            
        Returns:
            List[Dict[str, Any]]: Lista de productos destacados
        """
        catalog = await get_catalog()
        
        # Filtrar productos destacados (podría basarse en un campo específico)
        featured = [
            product for product in catalog
            if product.get("featured", False)
        ]
        
        # Si no hay suficientes productos destacados, tomar los más recientes
        if len(featured) < limit:
            # Ordenar por fecha de creación si está disponible
            catalog.sort(
                key=lambda x: x.get("created_at", ""),
                reverse=True
            )
            featured = catalog[:limit]
        
        return featured[:limit]
    
    async def _fetch_products(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los productos desde la API de Tienda Nube.
        
        Returns:
            List[Dict[str, Any]]: Lista de productos
        """
        headers = {
            "Authentication": f"bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        products = []
        page = 1
        has_more = True
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while has_more:
                try:
                    response = await client.get(
                        f"{self.base_url}/products",
                        headers=headers,
                        params={"page": page, "per_page": 50}
                    )
                    response.raise_for_status()
                    
                    page_products = response.json()
                    if not page_products:
                        has_more = False
                    else:
                        products.extend(page_products)
                        page += 1
                
                except httpx.HTTPStatusError as e:
                    logger.error(f"Error HTTP obteniendo productos: {e.response.status_code}")
                    raise
                except Exception as e:
                    logger.error(f"Error obteniendo productos: {str(e)}")
                    raise
        
        return products
    
    async def _fetch_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un producto específico desde la API de Tienda Nube.
        
        Args:
            product_id: ID del producto
            
        Returns:
            Optional[Dict[str, Any]]: Detalles del producto o None si no existe
        """
        headers = {
            "Authentication": f"bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/products/{product_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                return response.json()
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Error HTTP obteniendo producto {product_id}: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Error obteniendo producto {product_id}: {str(e)}")
            raise


# Importar httpx aquí para evitar dependencias circulares
import httpx
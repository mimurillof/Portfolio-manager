"""
Cliente de Supabase para consultas a la base de datos.
Maneja la lectura de usuarios, portfolios y assets desde las tablas relacionales.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from config import SupabaseConfig

try:
    from supabase import Client, create_client
except Exception:
    Client = Any  # type: ignore
    create_client = None  # type: ignore


logger = logging.getLogger(__name__)


class SupabaseDBClient:
    """Cliente para realizar queries a las tablas de Supabase."""

    def __init__(self) -> None:
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        """Obtiene o crea una instancia del cliente de Supabase."""
        if self._client is not None:
            return self._client

        if not SupabaseConfig.is_configured():
            raise RuntimeError("Supabase no está configurado correctamente. Revisa las variables de entorno.")

        if create_client is None:
            raise RuntimeError(
                "La librería 'supabase' no está instalada. Ejecuta 'pip install -r requirements.txt'."
            )

        self._client = create_client(
            SupabaseConfig.SUPABASE_URL,
            SupabaseConfig.get_supabase_key(),
        )
        logger.info("Cliente de Supabase inicializado correctamente.")
        return self._client

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios de la tabla 'users'.
        
        Returns:
            Lista de diccionarios con los datos de usuarios.
            Cada usuario tiene: user_id (uuid), first_name, last_name, email
        """
        try:
            client = self._get_client()
            response = client.table("users").select("*").execute()
            
            if not response.data:
                logger.warning("No se encontraron usuarios en la base de datos.")
                return []
            
            logger.info(f"Se encontraron {len(response.data)} usuarios.")
            return response.data
        
        except Exception as e:
            logger.error(f"Error al obtener usuarios: {e}")
            raise

    def get_user_portfolios(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los portfolios de un usuario específico.
        
        Args:
            user_id: UUID del usuario
        
        Returns:
            Lista de portfolios. Cada portfolio tiene: portfolio_id, portfolio_name, 
            description, created_at
        """
        try:
            client = self._get_client()
            response = (
                client.table("portfolios")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            
            if not response.data:
                logger.warning(f"No se encontraron portfolios para el usuario {user_id}")
                return []
            
            logger.info(f"Usuario {user_id}: {len(response.data)} portfolio(s) encontrado(s).")
            return response.data
        
        except Exception as e:
            logger.error(f"Error al obtener portfolios del usuario {user_id}: {e}")
            raise

    def get_portfolio_assets(self, portfolio_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todos los assets de un portfolio específico.
        
        Args:
            portfolio_id: ID del portfolio
        
        Returns:
            Lista de assets. Cada asset tiene: asset_id, asset_symbol, quantity,
            acquisition_price, acquisition_date
        """
        try:
            client = self._get_client()
            response = (
                client.table("assets")
                .select("*")
                .eq("portfolio_id", portfolio_id)
                .execute()
            )
            
            if not response.data:
                logger.warning(f"No se encontraron assets para el portfolio {portfolio_id}")
                return []
            
            logger.info(f"Portfolio {portfolio_id}: {len(response.data)} asset(s) encontrado(s).")
            return response.data
        
        except Exception as e:
            logger.error(f"Error al obtener assets del portfolio {portfolio_id}: {e}")
            raise

    def get_user_full_data(self, user_id: str) -> Dict[str, Any]:
        """
        Obtiene todos los datos de un usuario incluyendo portfolios y assets.
        
        Args:
            user_id: UUID del usuario
        
        Returns:
            Diccionario con estructura completa:
            {
                "user": {...},
                "portfolios": [
                    {
                        "portfolio_info": {...},
                        "assets": [...]
                    }
                ]
            }
        """
        try:
            # Obtener datos del usuario
            client = self._get_client()
            user_response = (
                client.table("users")
                .select("*")
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            
            if not user_response.data:
                raise ValueError(f"Usuario {user_id} no encontrado.")
            
            # Obtener portfolios del usuario
            portfolios = self.get_user_portfolios(user_id)
            
            # Para cada portfolio, obtener sus assets
            portfolios_with_assets = []
            for portfolio in portfolios:
                portfolio_id = portfolio.get("portfolio_id")
                assets = self.get_portfolio_assets(portfolio_id)
                
                portfolios_with_assets.append({
                    "portfolio_info": portfolio,
                    "assets": assets
                })
            
            result = {
                "user": user_response.data,
                "portfolios": portfolios_with_assets
            }
            
            logger.info(
                f"Datos completos obtenidos para usuario {user_id}: "
                f"{len(portfolios_with_assets)} portfolio(s)."
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error al obtener datos completos del usuario {user_id}: {e}")
            raise

    def get_all_users_with_portfolios(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios con sus portfolios y assets.
        Útil para procesamiento batch.
        
        Returns:
            Lista de usuarios con estructura completa (ver get_user_full_data)
        """
        try:
            users = self.get_all_users()
            
            result = []
            for user in users:
                user_id = user.get("user_id")
                if not user_id:
                    logger.warning(f"Usuario sin user_id detectado: {user}")
                    continue
                
                try:
                    full_data = self.get_user_full_data(user_id)
                    result.append(full_data)
                except Exception as e:
                    logger.error(f"Error procesando usuario {user_id}: {e}. Continuando...")
                    continue
            
            logger.info(f"Procesamiento completo: {len(result)} usuarios con portfolios.")
            return result
        
        except Exception as e:
            logger.error(f"Error al obtener todos los usuarios con portfolios: {e}")
            raise

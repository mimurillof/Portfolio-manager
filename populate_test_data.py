"""
Script de ejemplo para poblar datos de prueba en Supabase.
Este script crea usuarios, portfolios y assets de muestra para testing.

ADVERTENCIA: Este script inserta datos reales en tu base de datos.
Solo ejecutar en entorno de desarrollo/testing.

Uso:
    python populate_test_data.py [--users N] [--clean]
"""
import argparse
import logging
import sys
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

from supabase_client import SupabaseDBClient
from config import get_logger

logger = get_logger(__name__)


class TestDataPopulator:
    """Genera y pobla datos de prueba en Supabase."""
    
    # Datos de ejemplo
    FIRST_NAMES = ["Juan", "María", "Carlos", "Ana", "Luis", "Elena", "Pedro", "Sofia"]
    LAST_NAMES = ["García", "Rodríguez", "Martínez", "López", "Hernández", "González"]
    
    PORTFOLIO_NAMES = [
        "Portfolio Principal",
        "Inversiones Largo Plazo",
        "Trading Activo",
        "Dividendos",
        "Tecnología"
    ]
    
    STOCK_SYMBOLS = [
        "AAPL", "MSFT", "GOOG", "AMZN", "TSLA",
        "META", "NVDA", "AMD", "NFLX", "DIS",
        "JPM", "V", "MA", "PYPL", "SQ"
    ]
    
    def __init__(self):
        """Inicializa el cliente de Supabase."""
        self.client = SupabaseDBClient()._get_client()
    
    def generate_test_users(self, count: int) -> List[Dict[str, Any]]:
        """
        Genera datos de usuarios de prueba.
        
        Args:
            count: Número de usuarios a generar
        
        Returns:
            Lista de diccionarios con datos de usuarios
        """
        users = []
        
        for i in range(count):
            first = random.choice(self.FIRST_NAMES)
            last = random.choice(self.LAST_NAMES)
            email = f"{first.lower()}.{last.lower()}{i}@example.com"
            
            # Fecha de nacimiento aleatoria (25-65 años)
            age = random.randint(25, 65)
            birth_date = datetime.now() - timedelta(days=age*365)
            
            users.append({
                "first_name": first,
                "last_name": last,
                "email": email,
                "birth_date": birth_date.date().isoformat(),
                "gender": random.choice(["male", "female"])
            })
        
        return users
    
    def insert_users(self, users: List[Dict[str, Any]]) -> List[str]:
        """
        Inserta usuarios en la tabla users.
        
        Args:
            users: Lista de datos de usuarios
        
        Returns:
            Lista de user_ids insertados
        """
        logger.info(f"Insertando {len(users)} usuarios...")
        
        try:
            response = self.client.table("users").insert(users).execute()
            
            user_ids = [user.get("user_id") for user in response.data]
            logger.info(f"✓ {len(user_ids)} usuarios insertados correctamente")
            
            return user_ids
        
        except Exception as e:
            logger.error(f"Error insertando usuarios: {e}")
            raise
    
    def generate_portfolios_for_user(
        self, 
        user_id: str, 
        count: int = None
    ) -> List[Dict[str, Any]]:
        """
        Genera portfolios para un usuario.
        
        Args:
            user_id: UUID del usuario
            count: Número de portfolios (aleatorio si None)
        
        Returns:
            Lista de datos de portfolios
        """
        if count is None:
            count = random.randint(1, 3)
        
        portfolios = []
        
        for i in range(count):
            name = self.PORTFOLIO_NAMES[i % len(self.PORTFOLIO_NAMES)]
            
            portfolios.append({
                "user_id": user_id,
                "portfolio_name": f"{name} {i+1}" if count > 1 else name,
                "description": f"Portfolio de prueba {i+1}"
            })
        
        return portfolios
    
    def insert_portfolios(self, portfolios: List[Dict[str, Any]]) -> List[int]:
        """
        Inserta portfolios en la tabla portfolios.
        
        Args:
            portfolios: Lista de datos de portfolios
        
        Returns:
            Lista de portfolio_ids insertados
        """
        logger.info(f"Insertando {len(portfolios)} portfolios...")
        
        try:
            response = self.client.table("portfolios").insert(portfolios).execute()
            
            portfolio_ids = [p.get("portfolio_id") for p in response.data]
            logger.info(f"✓ {len(portfolio_ids)} portfolios insertados")
            
            return portfolio_ids
        
        except Exception as e:
            logger.error(f"Error insertando portfolios: {e}")
            raise
    
    def generate_assets_for_portfolio(
        self, 
        portfolio_id: int, 
        count: int = None
    ) -> List[Dict[str, Any]]:
        """
        Genera assets para un portfolio.
        
        Args:
            portfolio_id: ID del portfolio
            count: Número de assets (aleatorio si None)
        
        Returns:
            Lista de datos de assets
        """
        if count is None:
            count = random.randint(3, 8)
        
        # Seleccionar symbols únicos
        selected_symbols = random.sample(self.STOCK_SYMBOLS, min(count, len(self.STOCK_SYMBOLS)))
        
        assets = []
        
        for symbol in selected_symbols:
            quantity = round(random.uniform(5, 50), 2)
            price = round(random.uniform(50, 500), 2)
            
            # Fecha de adquisición (últimos 2 años)
            days_ago = random.randint(0, 730)
            acq_date = datetime.now() - timedelta(days=days_ago)
            
            assets.append({
                "portfolio_id": portfolio_id,
                "asset_symbol": symbol,
                "quantity": quantity,
                "acquisition_price": price,
                "acquisition_date": acq_date.date().isoformat()
            })
        
        return assets
    
    def insert_assets(self, assets: List[Dict[str, Any]]) -> List[int]:
        """
        Inserta assets en la tabla assets.
        
        Args:
            assets: Lista de datos de assets
        
        Returns:
            Lista de asset_ids insertados
        """
        logger.info(f"Insertando {len(assets)} assets...")
        
        try:
            response = self.client.table("assets").insert(assets).execute()
            
            asset_ids = [a.get("asset_id") for a in response.data]
            logger.info(f"✓ {len(asset_ids)} assets insertados")
            
            return asset_ids
        
        except Exception as e:
            logger.error(f"Error insertando assets: {e}")
            raise
    
    def populate(self, num_users: int = 5) -> Dict[str, Any]:
        """
        Puebla la base de datos con datos de prueba completos.
        
        Args:
            num_users: Número de usuarios a crear
        
        Returns:
            Diccionario con resumen de la operación
        """
        logger.info("=" * 70)
        logger.info("POBLANDO BASE DE DATOS CON DATOS DE PRUEBA")
        logger.info("=" * 70)
        
        summary = {
            "users_created": 0,
            "portfolios_created": 0,
            "assets_created": 0,
            "errors": []
        }
        
        try:
            # 1. Crear usuarios
            users_data = self.generate_test_users(num_users)
            user_ids = self.insert_users(users_data)
            summary["users_created"] = len(user_ids)
            
            # 2. Para cada usuario, crear portfolios y assets
            for user_id in user_ids:
                try:
                    # Crear portfolios
                    portfolios_data = self.generate_portfolios_for_user(user_id)
                    portfolio_ids = self.insert_portfolios(portfolios_data)
                    summary["portfolios_created"] += len(portfolio_ids)
                    
                    # Para cada portfolio, crear assets
                    for portfolio_id in portfolio_ids:
                        assets_data = self.generate_assets_for_portfolio(portfolio_id)
                        asset_ids = self.insert_assets(assets_data)
                        summary["assets_created"] += len(asset_ids)
                
                except Exception as e:
                    error_msg = f"Error procesando usuario {user_id}: {e}"
                    logger.error(error_msg)
                    summary["errors"].append(error_msg)
            
            logger.info("\n" + "=" * 70)
            logger.info("RESUMEN DE POBLACIÓN")
            logger.info("=" * 70)
            logger.info(f"Usuarios creados:   {summary['users_created']}")
            logger.info(f"Portfolios creados: {summary['portfolios_created']}")
            logger.info(f"Assets creados:     {summary['assets_created']}")
            logger.info(f"Errores:            {len(summary['errors'])}")
            logger.info("=" * 70)
            
            return summary
        
        except Exception as e:
            logger.error(f"Error crítico poblando datos: {e}", exc_info=True)
            raise
    
    def clean_test_data(self):
        """
        ADVERTENCIA: Elimina TODOS los datos de las tablas.
        Solo usar en entorno de testing.
        """
        logger.warning("⚠️  ELIMINANDO TODOS LOS DATOS DE PRUEBA...")
        
        try:
            # Eliminar en orden por dependencias
            self.client.table("assets").delete().neq("asset_id", 0).execute()
            logger.info("✓ Assets eliminados")
            
            self.client.table("portfolios").delete().neq("portfolio_id", 0).execute()
            logger.info("✓ Portfolios eliminados")
            
            self.client.table("users").delete().neq("user_id", "00000000-0000-0000-0000-000000000000").execute()
            logger.info("✓ Usuarios eliminados")
            
            logger.info("✓ Limpieza completada")
        
        except Exception as e:
            logger.error(f"Error limpiando datos: {e}")
            raise


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Puebla datos de prueba en Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--users',
        type=int,
        default=5,
        help='Número de usuarios a crear (default: 5)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='⚠️  ELIMINAR todos los datos antes de poblar (PELIGROSO)'
    )
    
    args = parser.parse_args()
    
    try:
        populator = TestDataPopulator()
        
        if args.clean:
            confirm = input("⚠️  ¿CONFIRMAS ELIMINAR TODOS LOS DATOS? (escribe 'SI'): ")
            if confirm == "SI":
                populator.clean_test_data()
            else:
                logger.info("Operación cancelada.")
                sys.exit(0)
        
        summary = populator.populate(args.users)
        
        if summary["errors"]:
            logger.warning("Población completó con errores.")
            sys.exit(1)
        else:
            logger.info("✓ Población completada exitosamente.")
            sys.exit(0)
    
    except KeyboardInterrupt:
        logger.warning("\nOperación interrumpida por el usuario.")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Error crítico: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

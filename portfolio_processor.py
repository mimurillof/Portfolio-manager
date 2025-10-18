"""
Procesador de portfolios para múltiples clientes.
Coordina la obtención de datos desde Supabase y la generación de reportes individuales.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from supabase_client import SupabaseDBClient
from portfolio_manager import PortfolioManager
from ticker_normalizer import TickerNormalizer
from config import get_logger

logger = get_logger(__name__)


class PortfolioProcessor:
    """Procesador batch de portfolios para múltiples clientes."""

    def __init__(self):
        """Inicializa el procesador con cliente de DB y portfolio manager."""
        self.db_client = SupabaseDBClient()
        self.portfolio_manager = PortfolioManager()
        
    def _transform_assets_format(self, db_assets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transforma los assets desde el formato de BD al formato esperado por PortfolioManager.
        Incluye normalización de símbolos de tickers.
        
        Formato BD:
            - asset_symbol: str
            - quantity: numeric
            - acquisition_price: numeric
            - acquisition_date: date
        
        Formato esperado:
            - symbol: str (NORMALIZADO)
            - units: float
            - name: str (opcional, se resolverá después)
        
        Args:
            db_assets: Lista de assets desde la base de datos
        
        Returns:
            Lista de assets en formato compatible con PortfolioManager
        """
        transformed = []
        
        for asset in db_assets:
            if not isinstance(asset, dict):
                logger.warning(f"Asset inválido (no es diccionario): {asset}")
                continue
            
            symbol = asset.get("asset_symbol")
            quantity = asset.get("quantity")
            
            if not symbol or quantity is None:
                logger.warning(f"Asset incompleto (falta symbol o quantity): {asset}")
                continue
            
            # NORMALIZAR SÍMBOLO usando TickerNormalizer
            original_symbol = symbol
            normalized_symbol = TickerNormalizer.normalize(symbol)
            
            if original_symbol != normalized_symbol:
                logger.info(f"Ticker normalizado: {original_symbol} → {normalized_symbol}")
            
            # Validar que el símbolo normalizado sea válido
            if not TickerNormalizer.validate_symbol(normalized_symbol):
                logger.warning(f"Símbolo inválido después de normalización: {normalized_symbol} (original: {original_symbol})")
                continue
            
            transformed.append({
                "symbol": normalized_symbol,
                "units": float(quantity),
                "name": normalized_symbol,  # Se actualizará con datos reales de yfinance
                # Datos adicionales para referencia
                "acquisition_price": asset.get("acquisition_price"),
                "acquisition_date": asset.get("acquisition_date"),
                "original_symbol": original_symbol,  # Guardar símbolo original para trazabilidad
            })
        
        return transformed
    
    def process_user(
        self, 
        user_id: str, 
        period: str = "6mo",
        skip_if_no_assets: bool = True
    ) -> Dict[str, Any]:
        """
        Procesa el portfolio de un usuario específico.
        
        Args:
            user_id: UUID del usuario
            period: Periodo de análisis histórico
            skip_if_no_assets: Si True, omite usuarios sin assets
        
        Returns:
            Diccionario con resultado del procesamiento:
            {
                "user_id": str,
                "status": "success" | "error" | "skipped",
                "portfolios_processed": int,
                "message": str,
                "error": str (opcional)
            }
        """
        result = {
            "user_id": user_id,
            "status": "error",
            "portfolios_processed": 0,
            "assets_processed": 0,
            "message": "",
        }
        
        try:
            logger.info(f"=== Procesando usuario {user_id} ===")
            
            # Obtener datos completos del usuario
            user_data = self.db_client.get_user_full_data(user_id)
            
            user_info = user_data.get("user", {})
            portfolios = user_data.get("portfolios", [])
            
            user_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            logger.info(f"Usuario: {user_name} ({user_info.get('email', 'N/A')})")
            
            if not portfolios:
                result["status"] = "skipped"
                result["message"] = "Usuario sin portfolios"
                logger.warning(f"Usuario {user_id} no tiene portfolios. Omitiendo...")
                return result
            
            # Consolidar todos los assets de todos los portfolios del usuario
            all_assets = []
            for portfolio_data in portfolios:
                portfolio_info = portfolio_data.get("portfolio_info", {})
                assets = portfolio_data.get("assets", [])
                
                logger.info(
                    f"  Portfolio: {portfolio_info.get('portfolio_name', 'Sin nombre')} "
                    f"({len(assets)} assets)"
                )
                
                all_assets.extend(assets)
            
            if not all_assets:
                if skip_if_no_assets:
                    result["status"] = "skipped"
                    result["message"] = "Usuario sin assets en sus portfolios"
                    logger.warning(f"Usuario {user_id} no tiene assets. Omitiendo...")
                    return result
            
            # Transformar assets al formato esperado
            transformed_assets = self._transform_assets_format(all_assets)
            
            if not transformed_assets:
                result["status"] = "skipped"
                result["message"] = "No se pudieron transformar los assets"
                logger.warning(f"Usuario {user_id}: transformación de assets resultó vacía.")
                return result
            
            logger.info(f"Generando reporte con {len(transformed_assets)} assets únicos...")
            
            # Generar reporte completo usando PortfolioManager
            report = self.portfolio_manager.generate_full_report(
                period=period,
                assets_data=transformed_assets,
                user_id=user_id
            )
            
            result["status"] = "success"
            result["portfolios_processed"] = len(portfolios)
            result["assets_processed"] = len(transformed_assets)
            result["message"] = f"Reporte generado exitosamente"
            
            logger.info(
                f"✓ Usuario {user_id} procesado exitosamente: "
                f"{result['portfolios_processed']} portfolio(s), "
                f"{result['assets_processed']} asset(s)"
            )
            
            return result
        
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["message"] = f"Error al procesar usuario: {str(e)}"
            logger.error(f"✗ Error procesando usuario {user_id}: {e}", exc_info=True)
            return result
    
    def process_all_users(
        self, 
        period: str = "6mo",
        skip_if_no_assets: bool = True
    ) -> Dict[str, Any]:
        """
        Procesa todos los usuarios de la base de datos.
        
        Args:
            period: Periodo de análisis histórico
            skip_if_no_assets: Si True, omite usuarios sin assets
        
        Returns:
            Resumen de la ejecución:
            {
                "started_at": str,
                "completed_at": str,
                "total_users": int,
                "successful": int,
                "errors": int,
                "skipped": int,
                "details": [...]
            }
        """
        start_time = datetime.now()
        
        summary = {
            "started_at": start_time.isoformat(),
            "completed_at": "",
            "total_users": 0,
            "successful": 0,
            "errors": 0,
            "skipped": 0,
            "details": []
        }
        
        try:
            logger.info("=" * 70)
            logger.info("INICIANDO PROCESAMIENTO BATCH DE PORTFOLIOS")
            logger.info("=" * 70)
            
            # Obtener todos los usuarios
            users = self.db_client.get_all_users()
            summary["total_users"] = len(users)
            
            if not users:
                logger.warning("No se encontraron usuarios en la base de datos.")
                summary["completed_at"] = datetime.now().isoformat()
                return summary
            
            logger.info(f"Total de usuarios a procesar: {len(users)}\n")
            
            # Procesar cada usuario
            for idx, user in enumerate(users, 1):
                user_id = user.get("user_id")
                
                if not user_id:
                    logger.warning(f"Usuario #{idx} sin user_id. Omitiendo...")
                    summary["skipped"] += 1
                    continue
                
                logger.info(f"\n[{idx}/{len(users)}] Procesando usuario {user_id}...")
                
                result = self.process_user(
                    user_id=user_id,
                    period=period,
                    skip_if_no_assets=skip_if_no_assets
                )
                
                summary["details"].append(result)
                
                # Actualizar contadores
                if result["status"] == "success":
                    summary["successful"] += 1
                elif result["status"] == "error":
                    summary["errors"] += 1
                elif result["status"] == "skipped":
                    summary["skipped"] += 1
            
            # Finalizar
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            summary["completed_at"] = end_time.isoformat()
            
            logger.info("\n" + "=" * 70)
            logger.info("RESUMEN DE EJECUCIÓN")
            logger.info("=" * 70)
            logger.info(f"Total usuarios: {summary['total_users']}")
            logger.info(f"Exitosos:       {summary['successful']}")
            logger.info(f"Errores:        {summary['errors']}")
            logger.info(f"Omitidos:       {summary['skipped']}")
            logger.info(f"Duración:       {duration:.2f} segundos")
            logger.info("=" * 70)
            
            return summary
        
        except Exception as e:
            logger.error(f"Error crítico en procesamiento batch: {e}", exc_info=True)
            summary["completed_at"] = datetime.now().isoformat()
            raise

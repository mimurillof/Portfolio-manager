"""
Módulo para integración con FastAPI Backend
Este archivo proporciona funciones que el backend puede importar
"""
import logging
from typing import Dict, Optional

from portfolio_manager import PortfolioManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioAPIService:
    """Servicio para integración con API"""
    
    def __init__(self):
        self.manager = PortfolioManager()
    
    def get_portfolio_data(self, period: str = "6mo", force_refresh: bool = False) -> Dict:
        """
        Obtiene datos del portafolio para la API
        
        Args:
            period: Periodo de tiempo
            force_refresh: Forzar actualización de datos
        
        Returns:
            Diccionario con datos del portafolio
        """
        try:
            if force_refresh:
                logger.info("Generando nuevo reporte forzado...")
                return self.manager.generate_full_report(period=period)

            data = self.manager._load_existing_portfolio_data()  # pylint: disable=protected-access
            if not data:
                logger.info("No hay datos persistidos; generando nuevo reporte...")
                return self.manager.generate_full_report(period=period)

            needs_save = self._ensure_weekly_performance(data)

            if needs_save:
                try:
                    self.manager._save_portfolio_data(data)  # pylint: disable=protected-access
                except Exception as save_error:  # pragma: no cover - logging de falla
                    logger.warning(
                        "No se pudo actualizar datos persistidos con weekly_performance: %s",
                        save_error,
                    )

            return data

        except Exception as e:
            logger.error(f"Error obteniendo datos del portafolio: {e}")
            return {}
    
    def _ensure_weekly_performance(self, data: Dict) -> bool:
        """Garantiza que cada activo tenga datos de weekly_performance.

        Returns:
            bool: True si se realizaron cambios que requieren reescritura del archivo.
        """

        updated = False

        for key in ("assets", "allocation", "gainers", "losers"):
            asset_list = data.get(key)
            if not isinstance(asset_list, list):
                continue

            if self._update_assets_weekly_performance(asset_list):
                updated = True

        return updated

    def _update_assets_weekly_performance(self, assets_list) -> bool:
        """Actualiza weekly_performance en una lista de activos."""
        updated = False

        for asset in assets_list:
            if not isinstance(asset, dict):
                continue

            weekly_perf = asset.get("weekly_performance")

            if isinstance(weekly_perf, list) and len(weekly_perf) >= 2:
                continue

            symbol = asset.get("symbol")
            if not symbol:
                continue

            weekly_data = self.manager.data_fetcher.get_weekly_performance(symbol)

            if weekly_data and len(weekly_data) >= 2:
                asset["weekly_performance"] = weekly_data
                updated = True

        return updated
    
    def get_portfolio_summary(self) -> Dict:
        """
        Obtiene resumen rápido del portafolio
        
        Returns:
            Diccionario con resumen
        """
        try:
            return self.manager.get_portfolio_summary()
        except Exception as e:
            logger.error(f"Error obteniendo resumen: {e}")
            return {}
    
    def get_market_data(self) -> Dict:
        """
        Obtiene datos de mercado
        
        Returns:
            Diccionario con datos de mercado
        """
        try:
            return self.manager.get_market_data()
        except Exception as e:
            logger.error(f"Error obteniendo datos de mercado: {e}")
            return {}
    
    def get_chart_html(self, chart_type: str = "portfolio") -> Optional[str]:
        """
        Obtiene el HTML de un gráfico
        
        Args:
            chart_type: Tipo de gráfico ("portfolio", "allocation", o símbolo de activo)
        
        Returns:
            Contenido HTML del gráfico
        """
        try:
            chart_key = "portfolio_performance"
            if chart_type == "portfolio":
                chart_path = OUTPUT_FILES["portfolio_chart_html"]
            elif chart_type == "allocation":
                chart_path = OUTPUT_FILES["assets_charts_dir"] / "allocation_chart.html"
                chart_key = "allocation_chart"
            else:
                chart_path = OUTPUT_FILES["assets_charts_dir"] / f"{chart_type}_chart.html"
                chart_key = f"asset_{chart_type}_html"

            data = self.manager._load_existing_portfolio_data()  # pylint: disable=protected-access
            remote_map = (data or {}).get("charts", {}) if isinstance(data, dict) else {}
            remote_path = remote_map.get(f"{chart_key}_remote")
            remote_url = remote_map.get(f"{chart_key}_url")

            if remote_url:
                logger.info("Usando gráfico remoto público desde Supabase: %s", remote_url)
                return remote_url

            if remote_path:
                logger.info("Descargando gráfico remoto desde Supabase: %s", remote_path)
                content = self.manager.storage.download_chart_asset(remote_path)
                if content:
                    return content.decode("utf-8", errors="ignore")

            if not chart_path.exists():
                logger.warning(f"Gráfico no encontrado: {chart_path}")
                return None

            with open(chart_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        except Exception as e:
            logger.error(f"Error leyendo gráfico: {e}")
            return None
    
    def add_asset(self, symbol: str, units: int) -> Dict:
        """
        Agrega un activo al portafolio
        
        Args:
            symbol: Símbolo del activo
            units: Número de unidades
        
        Returns:
            Diccionario con resultado de la operación
        """
        try:
            self.manager.add_asset_to_portfolio(symbol, units)
            
            # Regenerar reporte
            report = self.manager.generate_full_report()
            
            return {
                "success": True,
                "message": f"Activo {symbol} agregado exitosamente",
                "portfolio": report
            }
        
        except Exception as e:
            logger.error(f"Error agregando activo: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def update_portfolio(self, assets: list) -> Dict:
        """
        Actualiza todo el portafolio
        
        Args:
            assets: Lista de activos con formato [{"symbol": str, "units": int, "name": str}]
        
        Returns:
            Diccionario con resultado
        """
        try:
            new_config = {"assets": assets}
            self.manager.update_portfolio_config(new_config)
            
            # Regenerar reporte
            report = self.manager.generate_full_report()
            
            return {
                "success": True,
                "message": "Portafolio actualizado exitosamente",
                "portfolio": report
            }
        
        except Exception as e:
            logger.error(f"Error actualizando portafolio: {e}")
            return {
                "success": False,
                "message": str(e)
            }


# Instancia global del servicio
portfolio_service = PortfolioAPIService()


# Funciones helper para el backend de FastAPI
def get_portfolio_data_for_api(period: str = "6mo", refresh: bool = False) -> Dict:
    """Función helper para obtener datos del portafolio"""
    return portfolio_service.get_portfolio_data(period=period, force_refresh=refresh)


def get_portfolio_summary_for_api() -> Dict:
    """Función helper para obtener resumen del portafolio"""
    return portfolio_service.get_portfolio_summary()


def get_market_data_for_api() -> Dict:
    """Función helper para obtener datos de mercado"""
    return portfolio_service.get_market_data()


def get_chart_html_for_api(chart_type: str) -> Optional[str]:
    """Función helper para obtener HTML de gráficos"""
    return portfolio_service.get_chart_html(chart_type=chart_type)


def add_asset_for_api(symbol: str, units: int) -> Dict:
    """Función helper para agregar activo"""
    return portfolio_service.add_asset(symbol, units)


def update_portfolio_for_api(assets: list) -> Dict:
    """Función helper para actualizar portafolio"""
    return portfolio_service.update_portfolio(assets)

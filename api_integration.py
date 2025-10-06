"""
Módulo para integración con FastAPI Backend
Este archivo proporciona funciones que el backend puede importar
"""
import json
from pathlib import Path
from typing import Dict, Optional
import logging

from portfolio_manager import PortfolioManager
from config import OUTPUT_FILES

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
            # Si se fuerza actualización o no existe el archivo, generar nuevo reporte
            if force_refresh or not OUTPUT_FILES["portfolio_data"].exists():
                logger.info("Generando nuevo reporte...")
                report = self.manager.generate_full_report(period=period)
                return report
            
            # Leer datos guardados
            with open(OUTPUT_FILES["portfolio_data"], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
        
        except Exception as e:
            logger.error(f"Error obteniendo datos del portafolio: {e}")
            return {}
    
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
            if chart_type == "portfolio":
                chart_path = OUTPUT_FILES["portfolio_chart_html"]
            elif chart_type == "allocation":
                chart_path = Path(OUTPUT_FILES["assets_charts_dir"]).parent / "allocation_chart.html"
            else:
                # Asumiendo que es un símbolo de activo
                chart_path = OUTPUT_FILES["assets_charts_dir"] / f"{chart_type}_chart.html"
            
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

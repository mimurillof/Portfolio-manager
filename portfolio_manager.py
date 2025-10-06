"""
Módulo principal del Portfolio Manager
Orquesta todas las operaciones y genera los archivos de salida
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime

from config import (
    PORTFOLIO_CONFIG, WATCHLIST, TIME_PERIODS, 
    CHART_CONFIG, OUTPUT_FILES
)
from data_fetcher import DataFetcher
from portfolio_calculator import PortfolioCalculator
from chart_generator import ChartGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioManager:
    """Clase principal para gestionar el portafolio"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.calculator = PortfolioCalculator(self.data_fetcher)
        self.chart_generator = ChartGenerator(CHART_CONFIG)
        self.portfolio_config = PORTFOLIO_CONFIG
        self.watchlist = WATCHLIST
    
    def generate_full_report(self, period: str = "6mo") -> Dict:
        """
        Genera un reporte completo del portafolio
        
        Args:
            period: Periodo de tiempo para análisis histórico
        
        Returns:
            Diccionario con todos los datos del reporte
        """
        logger.info("Iniciando generación de reporte completo...")
        
        # 1. Calcular valor actual del portafolio
        portfolio_summary = self.calculator.calculate_portfolio_value(
            self.portfolio_config["assets"]
        )
        
        logger.info(f"Valor del portafolio: ${portfolio_summary['total_value']:,.2f}")
        
        # 2. Calcular rendimiento histórico
        performance_df = self.calculator.calculate_portfolio_performance(
            self.portfolio_config["assets"],
            period=period
        )
        
        # 3. Calcular métricas adicionales
        metrics = self.calculator.calculate_portfolio_metrics(performance_df)
        
        # 4. Identificar ganadores y perdedores
        gainers, losers = self.calculator.get_top_gainers_losers(
            portfolio_summary["assets"]
        )
        
        # 5. Calcular distribución de activos
        allocation = self.calculator.calculate_asset_allocation(
            portfolio_summary["assets"]
        )
        
        # 6. Obtener datos de mercado (Watchlist)
        market_overview = self.calculator.get_market_overview(self.watchlist)
        
        # Separar watchlist por categorías
        market_gainers = [item for item in market_overview if item["change_percent"] > 0]
        market_losers = [item for item in market_overview if item["change_percent"] < 0]
        
        # Ordenar por mayor cambio
        market_gainers.sort(key=lambda x: x["change_percent"], reverse=True)
        market_losers.sort(key=lambda x: x["change_percent"])
        
        # 7. Generar gráficos
        self._generate_charts(performance_df, portfolio_summary["assets"])
        
        # 8. Compilar reporte completo
        report = {
            "generated_at": datetime.now().isoformat(),
            "period": period,
            "summary": {
                "total_value": portfolio_summary["total_value"],
                "total_change_percent": portfolio_summary["total_change_percent"],
                "total_change_absolute": portfolio_summary["total_change_absolute"],
                "timestamp": portfolio_summary["timestamp"],
            },
            "metrics": metrics,
            "assets": portfolio_summary["assets"],
            "allocation": allocation,
            "gainers": gainers,
            "losers": losers,
            "market_overview": {
                "all": market_overview,
                "gainers": market_gainers[:5],  # Top 5
                "losers": market_losers[:5],    # Top 5
                "most_viewed": market_overview[:4],  # Primeros 4
            },
            "charts": {
                "portfolio_performance": str(OUTPUT_FILES["portfolio_chart_html"]),
                "portfolio_performance_png": str(OUTPUT_FILES["portfolio_chart_png"]),
            }
        }
        
        # 9. Guardar datos en JSON
        self._save_portfolio_data(report)
        
        logger.info("Reporte completo generado exitosamente")
        
        return report
    
    def _generate_charts(self, performance_df, assets_data: List[Dict]) -> None:
        """
        Genera todos los gráficos necesarios
        
        Args:
            performance_df: DataFrame con rendimiento del portafolio
            assets_data: Lista de datos de activos
        """
        logger.info("Generando gráficos...")
        
        # Gráfico principal del portafolio
        self.chart_generator.create_portfolio_performance_chart(
            performance_df,
            OUTPUT_FILES["portfolio_chart_html"],
            OUTPUT_FILES["portfolio_chart_png"]
        )
        
        # Gráficos individuales de cada activo
        assets_charts_dir = OUTPUT_FILES["assets_charts_dir"]
        
        for asset in assets_data:
            symbol = asset["symbol"]

            intraday_attempts = [
                ("60d", "15m"),
                ("30d", "15m"),
                ("30d", "30m"),
                ("30d", "1h"),
            ]

            intraday_data = None
            intraday_interval = None

            for period, interval in intraday_attempts:
                intraday_data = self.data_fetcher.get_stock_data(symbol, period=period, interval=interval)
                if intraday_data is not None and not intraday_data.empty:
                    intraday_interval = interval
                    break

            daily_data = self.data_fetcher.get_stock_data(symbol, period="6mo", interval="1d")

            if (
                (intraday_data is None or intraday_data.empty)
                and (daily_data is None or daily_data.empty)
            ):
                logger.warning("No se pudieron obtener datos históricos para %s", symbol)
                continue

            output_html = assets_charts_dir / f"{symbol}_chart.html"
            output_png = assets_charts_dir / f"{symbol}_chart.png"

            self.chart_generator.create_asset_chart(
                symbol,
                intraday_data,
                output_html,
                output_png,
                daily_data=daily_data,
                intraday_interval=intraday_interval,
            )
        
        # Gráfico de distribución
        allocation = self.calculator.calculate_asset_allocation(assets_data)
        allocation_html = Path(OUTPUT_FILES["assets_charts_dir"]).parent / "allocation_chart.html"
        allocation_png = Path(OUTPUT_FILES["assets_charts_dir"]).parent / "allocation_chart.png"
        
        self.chart_generator.create_allocation_pie_chart(
            allocation,
            allocation_html,
            allocation_png
        )
        
        logger.info("Gráficos generados exitosamente")
    
    def _save_portfolio_data(self, report: Dict) -> None:
        """
        Guarda los datos del portafolio en JSON
        
        Args:
            report: Diccionario con el reporte completo
        """
        try:
            with open(OUTPUT_FILES["portfolio_data"], 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Datos guardados en: {OUTPUT_FILES['portfolio_data']}")
        
        except Exception as e:
            logger.error(f"Error guardando datos: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """
        Obtiene un resumen rápido del portafolio sin generar gráficos
        
        Returns:
            Diccionario con resumen del portafolio
        """
        portfolio_summary = self.calculator.calculate_portfolio_value(
            self.portfolio_config["assets"]
        )
        
        return {
            "total_value": portfolio_summary["total_value"],
            "total_change_percent": portfolio_summary["total_change_percent"],
            "total_change_absolute": portfolio_summary["total_change_absolute"],
            "assets": portfolio_summary["assets"],
            "timestamp": portfolio_summary["timestamp"],
        }
    
    def get_market_data(self) -> Dict:
        """
        Obtiene datos del mercado (watchlist)
        
        Returns:
            Diccionario con datos de mercado
        """
        market_overview = self.calculator.get_market_overview(self.watchlist)
        
        market_gainers = [item for item in market_overview if item["change_percent"] > 0]
        market_losers = [item for item in market_overview if item["change_percent"] < 0]
        
        market_gainers.sort(key=lambda x: x["change_percent"], reverse=True)
        market_losers.sort(key=lambda x: x["change_percent"])
        
        return {
            "all": market_overview,
            "gainers": market_gainers[:5],
            "losers": market_losers[:5],
            "most_viewed": market_overview[:4],
            "timestamp": datetime.now().isoformat(),
        }
    
    def update_portfolio_config(self, new_config: Dict) -> None:
        """
        Actualiza la configuración del portafolio
        
        Args:
            new_config: Nueva configuración
        """
        self.portfolio_config = new_config
        logger.info("Configuración del portafolio actualizada")
    
    def add_asset_to_portfolio(self, symbol: str, units: int, name: Optional[str] = None) -> None:
        """
        Agrega un activo al portafolio
        
        Args:
            symbol: Símbolo del activo
            units: Número de unidades
            name: Nombre del activo (opcional)
        """
        if name is None:
            info = self.data_fetcher.get_stock_info(symbol)
            name = info.get("name", symbol)
        
        self.portfolio_config["assets"].append({
            "symbol": symbol,
            "units": units,
            "name": name
        })
        
        logger.info(f"Activo {symbol} agregado al portafolio")


# Función principal para ejecutar desde línea de comandos
def main():
    """Función principal"""
    manager = PortfolioManager()
    
    # Generar reporte completo
    report = manager.generate_full_report(period="6mo")
    
    # Imprimir resumen
    print("\n" + "="*60)
    print("RESUMEN DEL PORTAFOLIO")
    print("="*60)
    print(f"Valor Total: ${report['summary']['total_value']:,.2f}")
    print(f"Cambio: {report['summary']['total_change_percent']:+.2f}% (${report['summary']['total_change_absolute']:+,.2f})")
    print("\n" + "="*60)
    print("ACTIVOS")
    print("="*60)
    
    for asset in report['assets']:
        print(f"{asset['symbol']:6} | ${asset['current_price']:8.2f} | {asset['change_percent']:+6.2f}% | {asset['units']} units | ${asset['position_value']:,.2f}")
    
    print("\n" + "="*60)
    print("Reporte completo guardado en:", OUTPUT_FILES["portfolio_data"])
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

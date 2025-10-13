"""
Módulo principal del Portfolio Manager
Orquesta todas las operaciones y genera los archivos de salida
"""
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from numbers import Real

from config import (
    PORTFOLIO_CONFIG,
    WATCHLIST,
    TIME_PERIODS,
    CHART_CONFIG,
    OUTPUT_FILES,
)
from data_fetcher import DataFetcher
from portfolio_calculator import PortfolioCalculator
from chart_generator import ChartGenerator
from supabase_storage import SupabaseStorage

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
        self.storage = SupabaseStorage()
    
        self._existing_portfolio_data: Optional[Dict] = None
    
    def _load_existing_portfolio_data(self) -> Optional[Dict]:
        if self._existing_portfolio_data is not None:
            return self._existing_portfolio_data

        try:
            data = self.storage.load_portfolio_json()
            if data:
                self._existing_portfolio_data = data
                return data
        except Exception as exc:
            logger.warning("No se pudo cargar datos desde Supabase: %s", exc)

        portfolio_path = OUTPUT_FILES.get("portfolio_data")
        if portfolio_path and Path(portfolio_path).is_file():
            try:
                with open(portfolio_path, "r", encoding="utf-8") as fp:
                    self._existing_portfolio_data = json.load(fp)
                    return self._existing_portfolio_data
            except Exception as exc:
                logger.debug("No se pudo cargar portfolio_data local: %s", exc)
        return None

    def generate_full_report(self, period: str = "6mo") -> Dict[str, Any]:
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
        
        # Enriquecer allocation, ganadores y perdedores con weekly_performance si falta
        weekly_map = {
            asset["symbol"]: asset.get("weekly_performance")
            for asset in portfolio_summary["assets"]
            if isinstance(asset, dict)
        }

        def _inject_weekly(data_list: List[Dict]) -> None:
            for entry in data_list:
                if not isinstance(entry, dict):
                    continue
                weekly = entry.get("weekly_performance")
                if isinstance(weekly, list) and len(weekly) >= 2:
                    continue
                symbol = entry.get("symbol")
                if symbol and weekly_map.get(symbol):
                    entry["weekly_performance"] = weekly_map[symbol]

        _inject_weekly(allocation)
        _inject_weekly(gainers)
        _inject_weekly(losers)

        # 6. Obtener datos de mercado (Watchlist)
        market_overview_sections = self.calculator.get_market_overview(
            self.watchlist or [],
            source_data=self._load_existing_portfolio_data(),
            use_persisted=False,
        )
        
        all_list = market_overview_sections.get("all", [])
        gainers_list = market_overview_sections.get("gainers", [])
        losers_list = market_overview_sections.get("losers", [])
        most_viewed_list = market_overview_sections.get("most_viewed") or all_list
        most_active_list = market_overview_sections.get("most_active") or all_list
        
        # 7. Generar gráficos
        generated_chart_paths = self._generate_charts(performance_df, portfolio_summary["assets"])
        
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
                "all": all_list,
                "gainers": gainers_list[:5],
                "losers": losers_list[:5],
                "most_viewed": most_viewed_list[:4],
                "most_active": most_active_list[:5],
            },
            "charts": generated_chart_paths,
        }
        
        # 9. Guardar datos en JSON/Supabase
        sanitized_report = self._sanitize_for_json(report)
        self._save_portfolio_data(sanitized_report)
        
        logger.info("Reporte completo generado exitosamente")
        
        return sanitized_report
    
    def _generate_charts(self, performance_df, assets_data: List[Dict]) -> Dict[str, str]:
        """
        Genera todos los gráficos necesarios
        
        Args:
            performance_df: DataFrame con rendimiento del portafolio
            assets_data: Lista de datos de activos
        Returns:
            Diccionario con rutas locales y remotas de gráficos
        """
        logger.info("Generando gráficos...")
        
        # Gráfico principal del portafolio
        self.chart_generator.create_portfolio_performance_chart(
            performance_df,
            OUTPUT_FILES["portfolio_chart_html"],
            OUTPUT_FILES["portfolio_chart_png"]
        )

        charts_map: Dict[str, str] = {
            "portfolio_performance": str(OUTPUT_FILES["portfolio_chart_html"]),
            "portfolio_performance_png": str(OUTPUT_FILES["portfolio_chart_png"]),
        }

        self._upload_chart_if_enabled("portfolio_performance", OUTPUT_FILES["portfolio_chart_html"], charts_map)
        self._upload_chart_if_enabled("portfolio_performance_png", OUTPUT_FILES["portfolio_chart_png"], charts_map)
        
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

            self._upload_chart_if_enabled(f"asset_{symbol}_html", output_html, charts_map)
            self._upload_chart_if_enabled(f"asset_{symbol}_png", output_png, charts_map)
        
        # Gráfico de distribución
        allocation = self.calculator.calculate_asset_allocation(assets_data)
        allocation_html = Path(OUTPUT_FILES["assets_charts_dir"]).parent / "allocation_chart.html"
        allocation_png = Path(OUTPUT_FILES["assets_charts_dir"]).parent / "allocation_chart.png"
        
        self.chart_generator.create_allocation_pie_chart(
            allocation,
            allocation_html,
            allocation_png
        )

        self._upload_chart_if_enabled("allocation_chart", allocation_html, charts_map)
        self._upload_chart_if_enabled("allocation_chart_png", allocation_png, charts_map)
        
        logger.info("Gráficos generados exitosamente")
        return charts_map

    def _upload_chart_if_enabled(self, key: str, path: Path, charts_map: Dict[str, str]) -> None:
        try:
            remote_info = self.storage.upload_chart_asset(path)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("No se pudo subir gráfico '%s' a Supabase: %s", key, exc)
            return

        if remote_info:
            charts_map[f"{key}_remote"] = remote_info.get("path", "")
            if remote_info.get("public_url"):
                charts_map[f"{key}_url"] = remote_info["public_url"]
    
    def _sanitize_for_json(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._sanitize_for_json(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self._sanitize_for_json(item) for item in value]
        if isinstance(value, bool):
            return value
        if isinstance(value, Real):
            numeric = float(value)
            if not math.isfinite(numeric):
                return None
            if isinstance(value, int):
                return int(value)
            return numeric
        return value

    def _save_portfolio_data(self, report: Dict[str, Any]) -> None:
        """
        Guarda los datos del portafolio en JSON
        
        Args:
            report: Diccionario con el reporte completo
        """
        try:
            self.storage.save_portfolio_json(report)
            logger.info("Datos guardados en Supabase")
            self._existing_portfolio_data = report
        except Exception as exc:
            logger.warning("No se pudo guardar en Supabase: %s", exc)
            try:
                with open(OUTPUT_FILES["portfolio_data"], 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Datos guardados localmente en: {OUTPUT_FILES['portfolio_data']}")
                self._existing_portfolio_data = report
            except Exception as local_exc:
                logger.error("Error guardando datos localmente: %s", local_exc)
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
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
    
    def get_market_data(self) -> Dict[str, Any]:
        """
        Obtiene datos del mercado (watchlist)
        
        Returns:
            Diccionario con datos de mercado
        """
        overview: Dict[str, Any] = self.calculator.get_market_overview(
            self.watchlist,
            use_persisted=False,
        )
        overview["timestamp"] = datetime.now().isoformat()
        return overview
    
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

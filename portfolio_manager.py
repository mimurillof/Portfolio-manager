"""
Módulo principal del Portfolio Manager
Orquesta todas las operaciones y genera los archivos de salida
"""
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
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
        self._current_user_id: Optional[str] = None
    
    def _load_existing_portfolio_data(self, user_id: Optional[str] = None) -> Optional[Dict]:
        """
        Carga datos existentes del portfolio, priorizando datos de Supabase.
        
        Args:
            user_id: UUID del usuario para cargar datos específicos
        """
        if self._existing_portfolio_data is not None and self._current_user_id == user_id:
            return self._existing_portfolio_data

        try:
            data = self.storage.load_portfolio_json(user_id)
            if data:
                self._existing_portfolio_data = data
                self._current_user_id = user_id
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

    def generate_full_report(
        self, 
        period: str = "6mo",
        assets_data: Optional[List[Dict]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte completo del portafolio
        
        Args:
            period: Periodo de tiempo para análisis histórico
            assets_data: Lista de assets del portfolio. Si no se proporciona, usa PORTFOLIO_CONFIG
            user_id: UUID del usuario (para almacenamiento en Supabase). Si no se proporciona,
                    usa estructura legacy
        
        Returns:
            Diccionario con todos los datos del reporte
        """
        logger.info("Iniciando generación de reporte completo...")
        
        # Determinar qué assets usar
        if assets_data is None:
            logger.info("Usando configuración hardcodeada de assets (PORTFOLIO_CONFIG)")
            assets_to_process = self.portfolio_config["assets"]
        else:
            logger.info(f"Usando assets dinámicos desde base de datos ({len(assets_data)} assets)")
            assets_to_process = assets_data
        
        # 1. Calcular valor actual del portafolio
        portfolio_summary = self.calculator.calculate_portfolio_value(
            assets_to_process
        )
        
        logger.info(f"Valor del portafolio: ${portfolio_summary['total_value']:,.2f}")
        
        # 2. Calcular rendimiento histórico
        performance_df = self.calculator.calculate_portfolio_performance(
            assets_to_process,
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
            source_data=self._load_existing_portfolio_data(user_id),
            use_persisted=False,
        )
        
        all_list = market_overview_sections.get("all", [])
        gainers_list = market_overview_sections.get("gainers", [])
        losers_list = market_overview_sections.get("losers", [])
        most_viewed_list = market_overview_sections.get("most_viewed") or all_list
        most_active_list = market_overview_sections.get("most_active") or all_list
        
        # 7. Generar gráficos (con user_id para storage dinámico)
        generated_chart_paths = self._generate_charts(
            performance_df, 
            portfolio_summary["assets"], 
            allocation,  # Pasar allocation ya calculado
            user_id
        )
        
        # 8. Compilar reporte completo
        report = {
            "generated_at": datetime.now().isoformat(),
            "period": period,
            "user_id": user_id,  # Incluir user_id en el reporte
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
        
        # 9. Guardar datos en JSON/Supabase (con user_id para storage dinámico)
        sanitized_report = self._sanitize_for_json(report)
        self._save_portfolio_data(sanitized_report, user_id)
        
        logger.info("Reporte completo generado exitosamente")
        
        return sanitized_report
    
    def _generate_charts(
        self, 
        performance_df, 
        assets_data: List[Dict],
        allocation: List[Dict],  # Ya calculado previamente
        user_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Genera todos los gráficos necesarios
        
        Args:
            performance_df: DataFrame con rendimiento del portafolio
            assets_data: Lista de datos de activos
            allocation: Distribución de activos ya calculada
            user_id: UUID del usuario (para almacenamiento dinámico)
        Returns:
            Diccionario con rutas locales y remotas de gráficos
        """
        logger.info("Generando gráficos...")
        
        # Gráfico principal del portafolio
        html_path, png_bytes = self.chart_generator.create_portfolio_performance_chart(
            performance_df,
            OUTPUT_FILES["portfolio_chart_html"],
            OUTPUT_FILES["portfolio_chart_png"]
        )

        charts_map: Dict[str, str] = {
            "portfolio_performance": str(OUTPUT_FILES["portfolio_chart_html"]),
        }
        
        # Upload HTML chart
        self._upload_chart_if_enabled("portfolio_performance", OUTPUT_FILES["portfolio_chart_html"], charts_map, user_id)
        # Upload PNG bytes directly to Supabase
        if png_bytes:
            self._upload_png_bytes_to_supabase("portfolio_performance", png_bytes, charts_map, user_id)
        else:
            logger.warning("No PNG bytes generated for portfolio performance chart")

        # Gráficos individuales de cada activo
        assets_charts_dir = OUTPUT_FILES["assets_charts_dir"]
        
        # Importar función de sanitización para usar en claves del charts_map
        from config import SupabaseConfig
        
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

            html_path, png_bytes = self.chart_generator.create_asset_chart(
                symbol,
                intraday_data,
                output_html,
                output_png,
                daily_data=daily_data,
                intraday_interval=intraday_interval,
            )

            # Usar símbolo sanitizado para las claves en charts_map (para consistencia con Supabase)
            sanitized_symbol = SupabaseConfig.sanitize_filename_for_storage(symbol)
            # Upload HTML chart
            self._upload_chart_if_enabled(f"asset_{sanitized_symbol}_html", output_html, charts_map, user_id)
            # Upload PNG bytes directly to Supabase
            if png_bytes:
                self._upload_png_bytes_to_supabase(f"asset_{sanitized_symbol}", png_bytes, charts_map, user_id)
            else:
                logger.warning(f"No PNG bytes generated for asset {symbol}")

        # Gráfico de distribución (usa allocation ya calculado en generate_full_report)
        allocation_html, allocation_png_bytes = self.chart_generator.create_allocation_pie_chart(
            allocation,  # Usar el allocation pasado como parámetro
            Path(OUTPUT_FILES["assets_charts_dir"]).parent / "allocation_chart.html",
            Path(OUTPUT_FILES["assets_charts_dir"]).parent / "allocation_chart.png"
        )
        
        # Upload HTML chart
        self._upload_chart_if_enabled("allocation_chart", Path(OUTPUT_FILES["assets_charts_dir"]).parent / "allocation_chart.html", charts_map, user_id)
        # Upload PNG bytes directly to Supabase
        if allocation_png_bytes:
            self._upload_png_bytes_to_supabase("allocation_chart", allocation_png_bytes, charts_map, user_id)
        else:
            logger.warning("No PNG bytes generated for allocation chart")
        
        logger.info("Gráficos generados exitosamente")
        return charts_map

    def _upload_png_bytes_to_supabase(
        self, 
        key: str, 
        png_bytes: bytes, 
        charts_map: Dict[str, str], 
        user_id: Optional[str] = None
    ) -> None:
        """
        Sube bytes de PNG directamente a Supabase Storage sin crear archivo local.
        
        Args:
            key: clave para identificar el gráfico
            png_bytes: bytes del archivo PNG
            charts_map: diccionario para almacenar información de rutas remotas
            user_id: UUID del usuario
        """
        try:
            # Importar aquí para evitar problemas con los paths de archivo
            from config import SupabaseConfig
            
            # Generar el nombre de archivo remoto basado en la clave
            # Si es un gráfico de activo, extraer el nombre del activo y generar el path correcto
            if key.startswith("asset_"):
                # Extraer el nombre del símbolo desde la clave (ej: "asset_NVD_F" -> "NVD-F")
                # Pero ya está sanitizado, así que usamos directamente el nombre sanitizado
                remote_path = SupabaseConfig.build_chart_path(f"{key.replace('asset_', '')}_chart.png", user_id)
            elif key == "portfolio_performance":
                remote_path = SupabaseConfig.build_chart_path("portfolio_chart.png", user_id)
            elif key == "allocation_chart":
                remote_path = SupabaseConfig.build_chart_path("allocation_chart.png", user_id)
            else:
                remote_path = SupabaseConfig.build_chart_path(f"{key}_chart.png", user_id)
            
            # Subir directamente al bucket
            remote_info = self.storage.upload_png_bytes(png_bytes, remote_path)
            
            if remote_info:
                charts_map[f"{key}_png_remote"] = remote_info.get("path", "")
                if remote_info.get("public_url"):
                    charts_map[f"{key}_png_url"] = remote_info["public_url"]
                
                logger.info(f"PNG subido exitosamente a: {remote_info.get('path', 'desconocido')}")
            else:
                logger.warning(f"No se pudo obtener información remota para {key} PNG")
                
        except Exception as exc:
            logger.error(f"No se pudo subir PNG bytes para '{key}' a Supabase: {exc}")

    def _upload_chart_if_enabled(
        self, 
        key: str, 
        path: Path, 
        charts_map: Dict[str, str],
        user_id: Optional[str] = None
    ) -> None:
        # Verificar que el archivo existe y no está vacío
        if not path.exists():
            logger.warning("Archivo de gráfico no existe, omitiendo subida: %s", path)
            return
        
        # Si es PNG, verificar que fue generado recientemente (menos de 5 minutos)
        # para evitar subir archivos obsoletos cuando la exportación falla
        if path.suffix.lower() == '.png':
            from datetime import datetime, timedelta
            file_modified = datetime.fromtimestamp(path.stat().st_mtime)
            now = datetime.now()
            
            # Si el archivo tiene más de 5 minutos, es obsoleto (no se regeneró)
            if now - file_modified > timedelta(minutes=5):
                logger.warning(
                    "Archivo PNG obsoleto (modificado %s), omitiendo subida: %s",
                    file_modified.strftime("%Y-%m-%d %H:%M:%S"),
                    path
                )
                return
        
        try:
            remote_info = self.storage.upload_chart_asset(path, user_id)
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

    def _save_portfolio_data(self, report: Dict[str, Any], user_id: Optional[str] = None) -> None:
        """
        Guarda los datos del portafolio en JSON
        
        Args:
            report: Diccionario con el reporte completo
            user_id: UUID del usuario (para estructura dinámica en Supabase)
        """
        try:
            self.storage.save_portfolio_json(report, user_id)
            logger.info("Datos guardados en Supabase")
            self._existing_portfolio_data = report
            self._current_user_id = user_id
        except Exception as exc:
            logger.warning("No se pudo guardar en Supabase: %s", exc)
            try:
                with open(OUTPUT_FILES["portfolio_data"], 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Datos guardados localmente en: {OUTPUT_FILES['portfolio_data']}")
                self._existing_portfolio_data = report
                self._current_user_id = user_id
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

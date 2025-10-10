#!/usr/bin/env python3
"""
Script para generar el reporte de Portfolio con web scraping de Yahoo Finance.
Este script actualiza el archivo portfolio_data.json con datos frescos del mercado.

Uso:
    python generate_report.py [periodo]
    
    periodo (opcional): 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    Por defecto: 6mo
"""
import sys
import time
import schedule
from datetime import datetime
import pytz
from portfolio_manager import PortfolioManager
from pathlib import Path
from config import get_logger

def main():
    """Genera un reporte completo del portfolio."""
    # Determinar el periodo
    period = "6mo"
    if len(sys.argv) > 1:
        period = sys.argv[1]
    
    print("=" * 80)
    print("GENERADOR DE REPORTE DE PORTFOLIO CON WEB SCRAPING")
    print("=" * 80)
    print(f"\nPeriodo seleccionado: {period}")
    print("\nIniciando generación del reporte...")
    print("   - Obteniendo datos de yfinance para el portfolio")
    print("   - Scrapeando Yahoo Finance para market movers")
    print("   - Enriqueciendo datos con logos y métricas")
    print("   - Generando gráficos de performance")
    print("   - Guardando todo en portfolio_data.json\n")
    
    try:
        # Crear instancia del Portfolio Manager
        manager = PortfolioManager()
        
        # Generar el reporte completo
        report = manager.generate_full_report(period=period)
        
        # Mostrar resumen
        print("\n" + "=" * 80)
        print("REPORTE GENERADO EXITOSAMENTE")
        print("=" * 80)
        
        summary = report.get("summary", {})
        print(f"\nValor Total: ${summary.get('total_value', 0):,.2f}")
        print(f"Cambio: {summary.get('total_change_percent', 0):+.2f}%")
        
        market_overview = report.get("market_overview", {})
        print("\nMarket Overview:")
        for section, items in market_overview.items():
            if isinstance(items, list):
                print(f"   - {section}: {len(items)} elementos")
        
        # Ubicación del archivo
        data_file = Path(__file__).parent / "data" / "portfolio_data.json"
        print(f"\nDatos guardados en: {data_file}")
        
        print(f"\nReporte generado a las {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


def is_market_hours():
    """
    Verifica si estamos en horario de mercado (NYSE).
    Horario: Lunes a Viernes, 9:30 AM - 4:00 PM ET
    """
    # Zona horaria de Nueva York
    ny_tz = pytz.timezone('America/New_York')
    now = datetime.now(ny_tz)
    
    # Verificar si es día laborable (0=Lunes, 4=Viernes)
    if now.weekday() > 4:  # Sábado o Domingo
        return False
    
    # Verificar si estamos en horario de mercado (9:30 AM - 4:00 PM)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now <= market_close


def run_worker():
    """
    Ejecuta el worker que genera reportes cada 15 minutos durante horario de mercado.
    """
    logger = get_logger(__name__)
    logger.info("Worker de Portfolio Manager iniciado")
    logger.info("Configuracion: Ejecutar cada 15 minutos durante horario de mercado")
    logger.info("Horario: Lunes-Viernes 9:30 AM - 4:00 PM ET")
    
    # Ejecutar inmediatamente si estamos en horario de mercado
    if is_market_hours():
        logger.info("Estamos en horario de mercado. Generando primer reporte...")
        main()
    else:
        logger.info("Fuera de horario de mercado. Esperando...")
    
    # Programar ejecución cada 15 minutos
    def scheduled_task():
        if is_market_hours():
            logger.info("Ejecutando generacion programada de reporte...")
            main()
        else:
            logger.info("Fuera de horario de mercado. Saltando ejecucion.")
    
    schedule.every(15).minutes.do(scheduled_task)
    
    logger.info("Entrando en bucle infinito. Presiona Ctrl+C para detener.")
    
    # Bucle infinito
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep corto para que schedule funcione con precisión

if __name__ == "__main__":
    # Si se pasa el argumento --worker, ejecutar en modo worker
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        run_worker()
    else:
        # Ejecutar una sola vez (modo manual)
        main()


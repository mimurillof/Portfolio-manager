#!/usr/bin/env python3
"""
Script para generar reportes de Portfolio usando el sistema multi-cliente.
Este script procesa todos los usuarios desde Supabase o un usuario específico.

Uso:
    python generate_report.py [opciones]
    
Opciones:
    --period PERIOD     Periodo de análisis (default: 6mo)
    --user-id UUID      Procesar solo un usuario específico
    --worker            Ejecutar en modo worker (cada 15 min durante horario de mercado)
    --skip-empty        Omitir usuarios sin assets
    
Ejemplos:
    python generate_report.py
    python generate_report.py --period 1y --skip-empty
    python generate_report.py --user-id UUID
    python generate_report.py --worker
"""
import sys
import time
import argparse
import schedule
from datetime import datetime
import pytz
from portfolio_processor import PortfolioProcessor
from pathlib import Path
from config import get_logger

logger = get_logger(__name__)


def main(period="6mo", user_id=None, skip_empty=True):
    """
    Genera reportes de portfolio usando el sistema multi-cliente.
    
    Args:
        period: Periodo de análisis histórico
        user_id: UUID del usuario específico (None = todos)
        skip_empty: Omitir usuarios sin assets
    """
    print("=" * 80)
    print("GENERADOR DE REPORTES DE PORTFOLIO - SISTEMA MULTI-CLIENTE")
    print("=" * 80)
    print(f"\nPeriodo seleccionado: {period}")
    print(f"Modo: {'Usuario específico' if user_id else 'Todos los usuarios'}")
    print("\nIniciando generación de reportes...")
    print("   - Leyendo usuarios desde Supabase")
    print("   - Normalizando símbolos de tickers")
    print("   - Obteniendo datos de yfinance")
    print("   - Generando gráficos individuales")
    print("   - Guardando en storage por usuario\n")
    
    try:
        # Crear instancia del procesador
        processor = PortfolioProcessor()
        
        # Procesar según el modo
        if user_id:
            # Modo: Usuario específico
            logger.info(f"Procesando usuario: {user_id}")
            result = processor.process_user(
                user_id=user_id,
                period=period,
                skip_if_no_assets=skip_empty
            )
            
            # Crear summary compatible
            summary = {
                "total_users": 1,
                "successful": 1 if result['status'] == 'success' else 0,
                "errors": 1 if result['status'] == 'error' else 0,
                "skipped": 1 if result['status'] == 'skipped' else 0,
                "details": [result]
            }
        else:
            # Modo: Todos los usuarios
            logger.info("Procesando todos los usuarios...")
            summary = processor.process_all_users(
                period=period,
                skip_if_no_assets=skip_empty
            )
        
        # Mostrar resumen
        print("\n" + "=" * 80)
        print("RESUMEN DE GENERACIÓN")
        print("=" * 80)
        print(f"\nTotal usuarios:  {summary.get('total_users', 0)}")
        print(f"Exitosos:        {summary.get('successful', 0)}")
        print(f"Errores:         {summary.get('errors', 0)}")
        print(f"Omitidos:        {summary.get('skipped', 0)}")
        
        # Detalles por usuario
        if summary.get('details'):
            print("\nDetalles:")
            for detail in summary['details'][:5]:  # Mostrar max 5
                status_icon = "✓" if detail['status'] == 'success' else "✗" if detail['status'] == 'error' else "⊘"
                user_id_short = detail.get('user_id', 'N/A')[:8]
                portfolios = detail.get('portfolios_processed', 0)
                assets = detail.get('assets_processed', 0)
                print(f"  {status_icon} Usuario {user_id_short}... : {portfolios} portfolio(s), {assets} asset(s)")
        
        print(f"\nReporte generado a las {datetime.now().strftime('%H:%M:%S')}")
        
        # Retornar código de salida
        return 0 if summary.get('successful', 0) > 0 else 1
        
    except Exception as e:
        print(f"\nERROR: {e}")
        logger.error(f"Error crítico: {e}", exc_info=True)
        return 1


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


def run_worker(period="6mo", skip_empty=True):
    """
    Ejecuta el worker que genera reportes cada 15 minutos durante horario de mercado.
    
    Args:
        period: Periodo de análisis
        skip_empty: Omitir usuarios sin assets
    """
    logger.info("=" * 70)
    logger.info("WORKER DE PORTFOLIO MANAGER INICIADO")
    logger.info("=" * 70)
    logger.info("Configuración:")
    logger.info("  - Ejecutar cada 15 minutos durante horario de mercado")
    logger.info("  - Horario: Lunes-Viernes 9:30 AM - 4:00 PM ET")
    logger.info(f"  - Periodo: {period}")
    logger.info(f"  - Omitir usuarios sin assets: {skip_empty}")
    
    # Ejecutar inmediatamente si estamos en horario de mercado
    if is_market_hours():
        logger.info("\n✓ Estamos en horario de mercado. Generando primer reporte...")
        main(period=period, skip_empty=skip_empty)
    else:
        logger.info("\n⊘ Fuera de horario de mercado. Esperando...")
    
    # Programar ejecución cada 15 minutos
    def scheduled_task():
        if is_market_hours():
            logger.info("\n" + "=" * 70)
            logger.info("EJECUTANDO GENERACIÓN PROGRAMADA")
            logger.info("=" * 70)
            main(period=period, skip_empty=skip_empty)
        else:
            logger.info("⊘ Fuera de horario de mercado. Saltando ejecución.")
    
    schedule.every(15).minutes.do(scheduled_task)
    
    logger.info("\n✓ Worker en ejecución. Presiona Ctrl+C para detener.\n")
    
    # Bucle infinito
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n⚠ Worker detenido por el usuario.")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genera reportes de portfolio desde Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Generar reportes para todos los usuarios
  python generate_report.py
  
  # Con periodo específico
  python generate_report.py --period 1y
  
  # Usuario específico
  python generate_report.py --user-id 550e8400-e29b-41d4-a716-446655440000
  
  # Modo worker (cada 15 min en horario de mercado)
  python generate_report.py --worker
        """
    )
    
    parser.add_argument(
        '--period',
        type=str,
        default='6mo',
        choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'ytd', 'max'],
        help='Periodo de análisis (default: 6mo)'
    )
    
    parser.add_argument(
        '--user-id',
        type=str,
        default=None,
        help='Procesar solo un usuario específico (UUID)'
    )
    
    parser.add_argument(
        '--worker',
        action='store_true',
        help='Ejecutar en modo worker (cada 15 min durante horario de mercado)'
    )
    
    parser.add_argument(
        '--skip-empty',
        action='store_true',
        default=True,
        help='Omitir usuarios sin assets (default: True)'
    )
    
    args = parser.parse_args()
    
    if args.worker:
        run_worker(period=args.period, skip_empty=args.skip_empty)
    else:
        exit_code = main(
            period=args.period,
            user_id=args.user_id,
            skip_empty=args.skip_empty
        )
        sys.exit(exit_code)


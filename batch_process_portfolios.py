#!/usr/bin/env python3
"""
Script para procesar portfolios de todos los clientes desde Supabase.
Este script lee los usuarios, sus portfolios y assets desde la base de datos,
genera reportes individuales, y los almacena en subcarpetas específicas por usuario.

Uso:
    python batch_process_portfolios.py [--period 6mo] [--skip-empty]
    
Argumentos:
    --period: Periodo de análisis histórico (default: 6mo)
              Opciones: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, ytd, max
    --skip-empty: Omitir usuarios sin assets en sus portfolios
    --user-id: Procesar solo un usuario específico (UUID)
"""
import argparse
import json
import sys
import logging
from datetime import datetime
from pathlib import Path

from portfolio_processor import PortfolioProcessor
from config import get_logger

logger = get_logger(__name__)


def setup_logging(verbose: bool = False):
    """Configura el sistema de logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def save_execution_summary(summary: dict, output_dir: Path = None):
    """
    Guarda el resumen de ejecución en un archivo JSON.
    
    Args:
        summary: Diccionario con el resumen de la ejecución
        output_dir: Directorio de salida (default: output/)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / "output"
    
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"batch_summary_{timestamp}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Resumen de ejecución guardado en: {output_file}")
    except Exception as e:
        logger.error(f"Error guardando resumen de ejecución: {e}")


def print_summary_table(summary: dict):
    """
    Imprime una tabla formateada con el resumen de ejecución.
    
    Args:
        summary: Diccionario con el resumen de la ejecución
    """
    print("\n" + "=" * 80)
    print("RESUMEN DE EJECUCIÓN - PROCESAMIENTO BATCH")
    print("=" * 80)
    print(f"Inicio:          {summary.get('started_at', 'N/A')}")
    print(f"Finalización:    {summary.get('completed_at', 'N/A')}")
    print(f"Total usuarios:  {summary.get('total_users', 0)}")
    print(f"Exitosos:        {summary.get('successful', 0)}")
    print(f"Errores:         {summary.get('errors', 0)}")
    print(f"Omitidos:        {summary.get('skipped', 0)}")
    print("=" * 80)
    
    # Detalles por usuario
    if summary.get('details'):
        print("\nDETALLE POR USUARIO:")
        print("-" * 80)
        print(f"{'Usuario ID':<40} {'Estado':<12} {'Portfolios':<12} {'Assets':<12}")
        print("-" * 80)
        
        for detail in summary['details']:
            user_id = detail.get('user_id', 'N/A')[:37] + "..."  # Truncar UUID
            status = detail.get('status', 'N/A')
            portfolios = detail.get('portfolios_processed', 0)
            assets = detail.get('assets_processed', 0)
            
            print(f"{user_id:<40} {status:<12} {portfolios:<12} {assets:<12}")
            
            # Mostrar mensaje de error si existe
            if detail.get('error'):
                print(f"  └─ Error: {detail['error'][:70]}...")
        
        print("-" * 80)
    print()


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Procesa portfolios de todos los clientes desde Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Procesar todos los usuarios con periodo de 6 meses
  python batch_process_portfolios.py
  
  # Procesar con periodo de 1 año, omitiendo usuarios sin assets
  python batch_process_portfolios.py --period 1y --skip-empty
  
  # Procesar un usuario específico
  python batch_process_portfolios.py --user-id 550e8400-e29b-41d4-a716-446655440000
  
  # Modo verbose para debugging
  python batch_process_portfolios.py --verbose
        """
    )
    
    parser.add_argument(
        '--period',
        type=str,
        default='6mo',
        choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'ytd', 'max'],
        help='Periodo de análisis histórico (default: 6mo)'
    )
    
    parser.add_argument(
        '--skip-empty',
        action='store_true',
        help='Omitir usuarios sin assets en sus portfolios'
    )
    
    parser.add_argument(
        '--user-id',
        type=str,
        default=None,
        help='Procesar solo un usuario específico (UUID)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Habilitar logging detallado (DEBUG)'
    )
    
    parser.add_argument(
        '--no-summary-file',
        action='store_true',
        help='No guardar archivo de resumen JSON'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(args.verbose)
    
    try:
        # Inicializar procesador
        processor = PortfolioProcessor()
        
        # Procesar
        if args.user_id:
            logger.info(f"Procesando usuario específico: {args.user_id}")
            result = processor.process_user(
                user_id=args.user_id,
                period=args.period,
                skip_if_no_assets=args.skip_empty
            )
            
            # Crear summary compatible
            summary = {
                "started_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat(),
                "total_users": 1,
                "successful": 1 if result['status'] == 'success' else 0,
                "errors": 1 if result['status'] == 'error' else 0,
                "skipped": 1 if result['status'] == 'skipped' else 0,
                "details": [result]
            }
        else:
            logger.info("Procesando todos los usuarios...")
            summary = processor.process_all_users(
                period=args.period,
                skip_if_no_assets=args.skip_empty
            )
        
        # Mostrar resumen
        print_summary_table(summary)
        
        # Guardar resumen en archivo
        if not args.no_summary_file:
            save_execution_summary(summary)
        
        # Código de salida basado en resultados
        if summary.get('errors', 0) > 0:
            logger.warning("El procesamiento completó con errores.")
            sys.exit(1)
        elif summary.get('successful', 0) == 0:
            logger.warning("No se procesó ningún usuario exitosamente.")
            sys.exit(2)
        else:
            logger.info("Procesamiento completado exitosamente.")
            sys.exit(0)
    
    except KeyboardInterrupt:
        logger.warning("\nProcesamiento interrumpido por el usuario.")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Error crítico en el procesamiento: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

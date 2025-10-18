#!/usr/bin/env python3
"""
Script LEGACY para generar reporte de portfolio usando datos hardcodeados.
Este script mantiene compatibilidad con el sistema anterior (usuario único).

⚠️ DEPRECATED: Usar generate_report.py o batch_process_portfolios.py en su lugar.

Uso:
    python generate_report_legacy.py [periodo]
"""
import sys
from datetime import datetime
from portfolio_manager import PortfolioManager
from pathlib import Path

def main(period="6mo"):
    """Genera un reporte completo del portfolio (modo legacy)."""
    print("=" * 80)
    print("⚠️  MODO LEGACY - DATOS HARDCODEADOS")
    print("=" * 80)
    print(f"\nPeriodo seleccionado: {period}")
    print("\n⚠️  Este script usa datos hardcodeados de config.PORTFOLIO_CONFIG")
    print("   Considera migrar a generate_report.py para usar datos dinámicos.")
    print("\nIniciando generación del reporte...")
    
    try:
        # Crear instancia del Portfolio Manager
        manager = PortfolioManager()
        
        # Generar el reporte completo (SIN pasar assets_data ni user_id)
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


if __name__ == "__main__":
    period = sys.argv[1] if len(sys.argv) > 1 else "6mo"
    main(period=period)

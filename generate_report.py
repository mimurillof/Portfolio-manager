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
from portfolio_manager import PortfolioManager
from pathlib import Path

def main():
    # Determinar el periodo
    period = "6mo"
    if len(sys.argv) > 1:
        period = sys.argv[1]
    
    print("=" * 80)
    print("📊 GENERADOR DE REPORTE DE PORTFOLIO CON WEB SCRAPING")
    print("=" * 80)
    print(f"\n🕐 Periodo seleccionado: {period}")
    print("\n🚀 Iniciando generación del reporte...")
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
        print("✅ REPORTE GENERADO EXITOSAMENTE")
        print("=" * 80)
        
        summary = report.get("summary", {})
        print(f"\n💰 Valor Total: ${summary.get('total_value', 0):,.2f}")
        print(f"📈 Cambio: {summary.get('total_change_percent', 0):+.2f}%")
        
        market_overview = report.get("market_overview", {})
        print("\n📊 Market Overview:")
        for section, items in market_overview.items():
            if isinstance(items, list):
                print(f"   • {section}: {len(items)} elementos")
        
        # Ubicación del archivo
        data_file = Path(__file__).parent / "data" / "portfolio_data.json"
        print(f"\n💾 Datos guardados en: {data_file}")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Iniciar backend: uvicorn mi-proyecto-backend.main:app --reload")
        print("   2. Iniciar frontend: npm run dev")
        print("   3. Verificar el componente Watchlist en el Dashboard")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


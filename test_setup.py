"""
Script de prueba para verificar la instalación y funcionamiento
"""
import sys
from pathlib import Path

def test_imports():
    """Prueba que todos los módulos se puedan importar"""
    print("🔍 Probando imports...")
    
    try:
        import yfinance
        print("✅ yfinance instalado")
    except ImportError:
        print("❌ yfinance NO instalado - Ejecutar: pip install yfinance")
        return False
    
    try:
        import pandas
        print("✅ pandas instalado")
    except ImportError:
        print("❌ pandas NO instalado - Ejecutar: pip install pandas")
        return False
    
    try:
        import plotly
        print("✅ plotly instalado")
    except ImportError:
        print("❌ plotly NO instalado - Ejecutar: pip install plotly")
        return False
    
    try:
        from config import PORTFOLIO_CONFIG, WATCHLIST
        print("✅ config.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando config: {e}")
        return False
    
    try:
        from data_fetcher import DataFetcher
        print("✅ data_fetcher.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando data_fetcher: {e}")
        return False
    
    try:
        from portfolio_calculator import PortfolioCalculator
        print("✅ portfolio_calculator.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando portfolio_calculator: {e}")
        return False
    
    try:
        from chart_generator import ChartGenerator
        print("✅ chart_generator.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando chart_generator: {e}")
        return False
    
    try:
        from portfolio_manager import PortfolioManager
        print("✅ portfolio_manager.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando portfolio_manager: {e}")
        return False
    
    try:
        from api_integration import PortfolioAPIService
        print("✅ api_integration.py importado correctamente")
    except Exception as e:
        print(f"❌ Error importando api_integration: {e}")
        return False
    
    return True


def test_data_fetcher():
    """Prueba la obtención de datos"""
    print("\n🔍 Probando obtención de datos...")
    
    try:
        from data_fetcher import DataFetcher
        
        fetcher = DataFetcher()
        
        # Probar obtener precio de Apple
        print("Obteniendo precio de AAPL...")
        price = fetcher.get_current_price("AAPL")
        
        if price:
            print(f"✅ Precio de AAPL: ${price:.2f}")
            return True
        else:
            print("❌ No se pudo obtener el precio de AAPL")
            return False
    
    except Exception as e:
        print(f"❌ Error en test de data_fetcher: {e}")
        return False


def test_directories():
    """Verifica que los directorios necesarios existan"""
    print("\n🔍 Verificando directorios...")
    
    try:
        from config import DATA_DIR, CHARTS_DIR, OUTPUT_DIR
        
        dirs = [DATA_DIR, CHARTS_DIR, OUTPUT_DIR]
        
        for dir_path in dirs:
            if dir_path.exists():
                print(f"✅ {dir_path.name}/ existe")
            else:
                print(f"⚠️  {dir_path.name}/ no existe, creando...")
                dir_path.mkdir(exist_ok=True, parents=True)
                print(f"✅ {dir_path.name}/ creado")
        
        return True
    
    except Exception as e:
        print(f"❌ Error verificando directorios: {e}")
        return False


def test_basic_functionality():
    """Prueba funcionalidad básica"""
    print("\n🔍 Probando funcionalidad básica...")
    
    try:
        from portfolio_manager import PortfolioManager
        
        manager = PortfolioManager()
        print("✅ PortfolioManager inicializado")
        
        # Probar obtener resumen
        print("Obteniendo resumen del portafolio...")
        summary = manager.get_portfolio_summary()
        
        if summary and "total_value" in summary:
            print(f"✅ Valor del portafolio: ${summary['total_value']:,.2f}")
            print(f"   Cambio: {summary['total_change_percent']:+.2f}%")
            return True
        else:
            print("❌ No se pudo obtener el resumen")
            return False
    
    except Exception as e:
        print(f"❌ Error en prueba de funcionalidad: {e}")
        return False


def main():
    """Función principal de pruebas"""
    print("="*60)
    print("PRUEBA DE PORTFOLIO MANAGER")
    print("="*60)
    
    all_tests_passed = True
    
    # Test 1: Imports
    if not test_imports():
        all_tests_passed = False
        print("\n⚠️  Instalar dependencias: pip install -r requirements.txt")
    
    # Test 2: Directorios
    if not test_directories():
        all_tests_passed = False
    
    # Test 3: Data Fetcher
    if not test_data_fetcher():
        all_tests_passed = False
        print("\n⚠️  Verificar conexión a internet")
    
    # Test 4: Funcionalidad básica
    if not test_basic_functionality():
        all_tests_passed = False
    
    # Resultado final
    print("\n" + "="*60)
    if all_tests_passed:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("="*60)
        print("\n🎉 El sistema está listo para usar!")
        print("\nEjecutar:")
        print("  python portfolio_manager.py    - Para generar reporte completo")
        print("  python portofolio.py           - Alias al comando anterior")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("="*60)
        print("\n⚠️  Por favor, corregir los errores antes de continuar")
    
    print()


if __name__ == "__main__":
    main()

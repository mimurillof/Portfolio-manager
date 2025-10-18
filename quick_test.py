#!/usr/bin/env python3
"""
Script de Quick Test para validar el sistema multi-cliente.
Ejecuta pruebas rápidas sin generar reportes completos.
"""
import sys
from pathlib import Path

def test_imports():
    """Verifica que todos los módulos se importen correctamente."""
    print("=" * 70)
    print("TEST 1: Importación de Módulos")
    print("=" * 70)
    
    try:
        from ticker_normalizer import TickerNormalizer
        print("✓ ticker_normalizer importado")
    except Exception as e:
        print(f"✗ Error importando ticker_normalizer: {e}")
        return False
    
    try:
        from supabase_client import SupabaseDBClient
        print("✓ supabase_client importado")
    except Exception as e:
        print(f"✗ Error importando supabase_client: {e}")
        return False
    
    try:
        from portfolio_processor import PortfolioProcessor
        print("✓ portfolio_processor importado")
    except Exception as e:
        print(f"✗ Error importando portfolio_processor: {e}")
        return False
    
    try:
        from portfolio_manager import PortfolioManager
        print("✓ portfolio_manager importado")
    except Exception as e:
        print(f"✗ Error importando portfolio_manager: {e}")
        return False
    
    print("\n✅ Todos los módulos importados exitosamente\n")
    return True


def test_ticker_normalizer():
    """Prueba el normalizador de tickers."""
    print("=" * 70)
    print("TEST 2: Normalización de Tickers")
    print("=" * 70)
    
    from ticker_normalizer import TickerNormalizer
    
    test_cases = [
        ("BTCUSD", "BTC-USD"),
        ("NVD.F", "NVDA"),
        ("AAPL", "AAPL"),
        ("BRK.B", "BRK-B"),
        ("ETHUSD", "ETH-USD"),
        ("  tsla  ", "TSLA"),
    ]
    
    all_passed = True
    
    for original, expected in test_cases:
        result = TickerNormalizer.normalize(original)
        status = "✓" if result == expected else "✗"
        
        if result != expected:
            all_passed = False
            print(f"{status} {original:15s} → {result:15s} (esperado: {expected})")
        else:
            print(f"{status} {original:15s} → {result}")
    
    if all_passed:
        print("\n✅ Todos los casos de prueba pasaron\n")
    else:
        print("\n✗ Algunos casos fallaron\n")
    
    return all_passed


def test_supabase_connection():
    """Verifica la conexión a Supabase."""
    print("=" * 70)
    print("TEST 3: Conexión a Supabase")
    print("=" * 70)
    
    try:
        from supabase_client import SupabaseDBClient
        from config import SupabaseConfig
        
        if not SupabaseConfig.is_configured():
            print("⚠️  Supabase no está configurado en .env")
            print("   Configura las variables de entorno:")
            print("   - SUPABASE_URL")
            print("   - SUPABASE_ANON_KEY o SUPABASE_SERVICE_ROLE_KEY")
            print("   - ENABLE_SUPABASE_UPLOAD=true")
            return False
        
        print("✓ Variables de entorno configuradas")
        
        client = SupabaseDBClient()
        users = client.get_all_users()
        
        print(f"✓ Conexión exitosa a Supabase")
        print(f"✓ Usuarios encontrados: {len(users)}")
        
        if len(users) == 0:
            print("\n⚠️  No hay usuarios en la base de datos")
            print("   Ejecuta: python populate_test_data.py --users 5")
        else:
            print("\n✅ Base de datos lista para procesar\n")
        
        return True
    
    except Exception as e:
        print(f"✗ Error conectando a Supabase: {e}")
        return False


def test_env_file():
    """Verifica que el archivo .env exista y tenga las variables necesarias."""
    print("=" * 70)
    print("TEST 4: Archivo .env")
    print("=" * 70)
    
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print("✗ Archivo .env no encontrado")
        print(f"   Esperado en: {env_path}")
        return False
    
    print(f"✓ Archivo .env encontrado: {env_path}")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_BUCKET_NAME",
    ]
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    missing = []
    for var in required_vars:
        if var not in content:
            missing.append(var)
        else:
            print(f"✓ {var} presente")
    
    if missing:
        print(f"\n⚠️  Variables faltantes: {', '.join(missing)}")
        return False
    
    print("\n✅ Archivo .env correctamente configurado\n")
    return True


def main():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 70)
    print("QUICK TEST - SISTEMA MULTI-CLIENTE PORTFOLIO MANAGER")
    print("=" * 70)
    print()
    
    results = []
    
    # Test 1: Importaciones
    results.append(("Importaciones", test_imports()))
    
    # Test 2: Normalizador
    results.append(("Normalizador", test_ticker_normalizer()))
    
    # Test 3: Archivo .env
    results.append(("Archivo .env", test_env_file()))
    
    # Test 4: Conexión Supabase
    results.append(("Conexión Supabase", test_supabase_connection()))
    
    # Resumen
    print("=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:12s} - {name}")
    
    print()
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("🎉 TODOS LOS TESTS PASARON")
        print("\nEl sistema está listo para ejecutar:")
        print("  python generate_report.py")
        print("\nO para procesar todos los usuarios:")
        print("  python batch_process_portfolios.py")
        return 0
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
        print("\nRevisa los errores anteriores y corrígelos antes de continuar.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

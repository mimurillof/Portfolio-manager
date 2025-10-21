"""
Script de prueba para verificar la sanitización de nombres de archivo.
"""
import sys
from pathlib import Path
from config import SupabaseConfig

def test_sanitization():
    """Prueba la sanitización de nombres de archivo."""
    
    test_cases = [
        ("^SPX_chart.html", "_CARET_SPX_chart.html"),
        ("^GSPC_chart.png", "_CARET_GSPC_chart.png"),
        ("BTC-USD_chart.html", "BTC-USD_chart.html"),  # Sin cambios
        ("AAPL_chart.html", "AAPL_chart.html"),        # Sin cambios
        ("test^file<name>.html", "test_CARET_file_LT_name_GT_.html"),
    ]
    
    print("=" * 80)
    print("TEST DE SANITIZACIÓN DE NOMBRES DE ARCHIVO")
    print("=" * 80)
    print()
    
    all_passed = True
    
    for original, expected in test_cases:
        result = SupabaseConfig.sanitize_filename_for_storage(original)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✓" if passed else "✗"
        print(f"{status} {original:30s} → {result:40s}", end="")
        
        if not passed:
            print(f" (esperado: {expected})")
        else:
            print()
    
    print()
    print("=" * 80)
    print("TEST DE RUTAS REMOTAS COMPLETAS")
    print("=" * 80)
    print()
    
    # Probar rutas completas
    test_paths = [
        Path("charts/assets/^SPX_chart.html"),
        Path("charts/portfolio_chart.html"),
        Path("charts/assets/BTC-USD_chart.png"),
    ]
    
    user_id = "test-user-123"
    
    for test_path in test_paths:
        remote_path = SupabaseConfig.remote_chart_path_for(test_path, user_id)
        print(f"  Local:  {test_path}")
        print(f"  Remote: {remote_path}")
        print()
    
    print("=" * 80)
    
    if all_passed:
        print("✓ TODAS LAS PRUEBAS PASARON")
        return 0
    else:
        print("✗ ALGUNAS PRUEBAS FALLARON")
        return 1

if __name__ == "__main__":
    sys.exit(test_sanitization())

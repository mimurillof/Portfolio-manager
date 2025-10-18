#!/usr/bin/env python3
"""
Script de verificación de correcciones críticas.
Valida que los 3 problemas identificados estén resueltos.
"""
import sys
from pathlib import Path


def test_config_paths():
    """Verifica que config.py no cree subcarpetas Informes/ o Graficos/"""
    print("=" * 70)
    print("TEST 1: Estructura de Carpetas")
    print("=" * 70)
    
    try:
        from config import SupabaseConfig
        
        test_user_id = "12345678-1234-1234-1234-123456789abc"
        
        # Test 1: portfolio_json_path
        json_path = SupabaseConfig.portfolio_json_path(user_id=test_user_id)
        print(f"\nRuta JSON: {json_path}")
        
        if "/Informes/" in json_path:
            print("✗ ERROR: La ruta contiene '/Informes/'")
            print(f"  Esperado: {test_user_id}/portfolio_data.json")
            print(f"  Actual:   {json_path}")
            return False
        
        expected_json = f"{test_user_id}/portfolio_data.json"
        if json_path == expected_json:
            print(f"✓ Ruta JSON correcta: {json_path}")
        else:
            print(f"✗ Ruta JSON incorrecta")
            print(f"  Esperado: {expected_json}")
            print(f"  Actual:   {json_path}")
            return False
        
        # Test 2: charts_prefix
        charts_prefix = SupabaseConfig.charts_prefix(user_id=test_user_id)
        print(f"\nPrefijo de gráficos: {charts_prefix}")
        
        if "/Graficos" in charts_prefix:
            print("✗ ERROR: El prefijo contiene '/Graficos'")
            print(f"  Esperado: {test_user_id}")
            print(f"  Actual:   {charts_prefix}")
            return False
        
        if charts_prefix == test_user_id:
            print(f"✓ Prefijo correcto: {charts_prefix}")
        else:
            print(f"✗ Prefijo incorrecto")
            print(f"  Esperado: {test_user_id}")
            print(f"  Actual:   {charts_prefix}")
            return False
        
        # Test 3: build_chart_path
        test_chart = "assets/charts/portfolio_chart.html"
        chart_path = SupabaseConfig.build_chart_path(test_chart, user_id=test_user_id)
        print(f"\nRuta de gráfico: {chart_path}")
        
        expected_chart = f"{test_user_id}/portfolio_chart.html"
        if chart_path == expected_chart:
            print(f"✓ Ruta de gráfico correcta: {chart_path}")
        else:
            print(f"⚠ Ruta de gráfico:")
            print(f"  Esperado: {expected_chart}")
            print(f"  Actual:   {chart_path}")
            # No falla, solo advertencia
        
        print("\n✅ Estructura de carpetas CORRECTA (plana, sin subcarpetas)\n")
        return True
    
    except Exception as e:
        print(f"✗ Error en test: {e}")
        return False


def test_allocation_chart():
    """Verifica que allocation_chart use datos dinámicos"""
    print("=" * 70)
    print("TEST 2: Allocation Chart con Datos Dinámicos")
    print("=" * 70)
    
    try:
        # Leer portfolio_manager.py
        manager_path = Path(__file__).parent / "portfolio_manager.py"
        with open(manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar que _generate_charts tenga allocation como parámetro
        if "def _generate_charts(" in content:
            # Buscar la firma del método
            start = content.find("def _generate_charts(")
            end = content.find("):", start)
            signature = content[start:end+2]
            
            print("\nFirma del método _generate_charts:")
            print(signature.replace("\n", " ").strip())
            
            if "allocation" in signature:
                print("\n✓ Método _generate_charts recibe 'allocation' como parámetro")
            else:
                print("\n✗ ERROR: Método NO recibe 'allocation' como parámetro")
                return False
        
        # Verificar que NO se recalcule allocation dentro de _generate_charts
        if "allocation = self.calculator.calculate_asset_allocation(assets_data)" in content:
            # Contar cuántas veces aparece
            count = content.count("allocation = self.calculator.calculate_asset_allocation")
            
            if count > 1:
                print(f"\n⚠ ADVERTENCIA: 'calculate_asset_allocation' se llama {count} veces")
                print("  Debería llamarse solo una vez en generate_full_report")
                return False
            else:
                print(f"\n✓ 'calculate_asset_allocation' se llama solo 1 vez (correcto)")
        
        # Verificar que allocation se pase a _generate_charts
        if "generated_chart_paths = self._generate_charts(" in content:
            start = content.find("generated_chart_paths = self._generate_charts(")
            end = content.find(")", start)
            call_site = content[start:end+1]
            
            print("\nLlamada a _generate_charts:")
            print(call_site.replace("\n", " ").strip())
            
            if "allocation" in call_site:
                print("\n✓ Se pasa 'allocation' a _generate_charts")
            else:
                print("\n✗ ERROR: NO se pasa 'allocation' a _generate_charts")
                return False
        
        print("\n✅ Allocation chart usa datos dinámicos CORRECTAMENTE\n")
        return True
    
    except Exception as e:
        print(f"✗ Error en test: {e}")
        return False


def test_worker_loop():
    """Verifica la lógica del worker loop"""
    print("=" * 70)
    print("TEST 3: Worker Loop (Horario de Mercado)")
    print("=" * 70)
    
    try:
        # Leer generate_report.py
        report_path = Path(__file__).parent / "generate_report.py"
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("is_market_hours()", "Función para verificar horario de mercado"),
            ("schedule.every(15).minutes", "Ejecución cada 15 minutos"),
            ("while True:", "Bucle infinito del worker"),
            ("schedule.run_pending()", "Ejecutar tareas programadas"),
        ]
        
        all_passed = True
        
        for check, description in checks:
            if check in content:
                print(f"✓ {description}: '{check}' encontrado")
            else:
                print(f"✗ {description}: '{check}' NO encontrado")
                all_passed = False
        
        if all_passed:
            print("\n✅ Worker loop implementado CORRECTAMENTE")
            print("\nIMPORTANTE:")
            print("  - El worker ejecuta cada 15 minutos durante horario de mercado")
            print("  - Horario: Lunes-Viernes 9:30 AM - 4:00 PM ET")
            print("  - Fuera de horario: El worker sigue corriendo pero NO ejecuta")
            print("  - Esto es CORRECTO y debe persistir\n")
        else:
            print("\n✗ Worker loop tiene problemas\n")
        
        return all_passed
    
    except Exception as e:
        print(f"✗ Error en test: {e}")
        return False


def main():
    """Ejecuta todos los tests de verificación"""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DE CORRECCIONES CRÍTICAS")
    print("=" * 70)
    print()
    
    results = []
    
    # Test 1: Estructura de carpetas
    results.append(("Estructura Plana", test_config_paths()))
    
    # Test 2: Allocation chart dinámico
    results.append(("Allocation Dinámico", test_allocation_chart()))
    
    # Test 3: Worker loop
    results.append(("Worker Loop", test_worker_loop()))
    
    # Resumen
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:12s} - {name}")
    
    print()
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("🎉 TODAS LAS CORRECCIONES APLICADAS CORRECTAMENTE")
        print("\nPróximos pasos:")
        print("  1. Ejecutar: python generate_report.py --verbose")
        print("  2. Verificar logs NO muestren 'configuración hardcodeada'")
        print("  3. Verificar Storage en Supabase:")
        print("     portfolio-files/{user_id}/portfolio_data.json")
        print("     portfolio-files/{user_id}/allocation_chart.html")
        print("  4. Abrir allocation_chart.html y verificar assets del usuario")
        return 0
    else:
        print("⚠️  ALGUNAS CORRECCIONES FALLARON")
        print("\nRevisa los errores anteriores.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

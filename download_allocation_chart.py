#!/usr/bin/env python3
"""
Script para descargar y verificar allocation_chart.html desde Supabase.
"""
from supabase_storage import SupabaseStorage
from pathlib import Path

def main():
    print("=" * 70)
    print("DESCARGANDO ALLOCATION_CHART DESDE SUPABASE")
    print("=" * 70)
    
    user_id = "238ff453-ab78-42de-9b54-a63980ff56e3"
    
    storage = SupabaseStorage()
    
    # Intentar descargar allocation_chart.html
    remote_path = f"{user_id}/allocation_chart.html"
    
    print(f"\nDescargando: portfolio-files/{remote_path}")
    
    try:
        # Descargar el contenido
        from supabase import create_client
        from config import SupabaseConfig
        
        # Usar la key disponible (anon_key o service_role_key)
        key = SupabaseConfig.SUPABASE_ANON_KEY or SupabaseConfig.SUPABASE_SERVICE_ROLE_KEY
        client = create_client(SupabaseConfig.SUPABASE_URL, key)
        
        response = client.storage.from_("portfolio-files").download(remote_path)
        
        # Guardar localmente
        output_path = Path("allocation_chart_verificacion.html")
        output_path.write_bytes(response)
        
        print(f"✓ Archivo descargado: {output_path}")
        print(f"✓ Tamaño: {len(response)} bytes")
        
        # Analizar contenido
        content = response.decode('utf-8')
        
        # Buscar símbolos hardcodeados
        hardcoded = ["TSLA", "MSFT", "AAPL", "AMZN", "GOOG"]
        found_hardcoded = [s for s in hardcoded if s in content]
        
        # Buscar símbolos del usuario
        user_symbols = ["PAXG-USD", "BTC-USD", "NVDA"]
        found_user = [s for s in user_symbols if s in content]
        
        print("\n" + "=" * 70)
        print("ANÁLISIS DEL CONTENIDO")
        print("=" * 70)
        
        if found_hardcoded:
            print(f"\n❌ SÍMBOLOS HARDCODEADOS ENCONTRADOS: {found_hardcoded}")
            print("   El archivo aún contiene datos antiguos")
        else:
            print(f"\n✓ No se encontraron símbolos hardcodeados")
        
        if found_user:
            print(f"\n✅ SÍMBOLOS DEL USUARIO ENCONTRADOS: {found_user}")
            print("   El archivo contiene los datos correctos")
        else:
            print(f"\n❌ No se encontraron símbolos del usuario")
        
        print(f"\n🌐 Abre el archivo en tu navegador:")
        print(f"   {output_path.absolute()}")
        
    except Exception as e:
        print(f"✗ Error descargando archivo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

#!/usr/bin/env python3
"""
Script para eliminar archivos PNG obsoletos de Supabase Storage.
"""
from supabase import create_client
from config import SupabaseConfig

def main():
    print("=" * 70)
    print("LIMPIANDO ARCHIVOS PNG OBSOLETOS DE SUPABASE STORAGE")
    print("=" * 70)
    
    user_id = "238ff453-ab78-42de-9b54-a63980ff56e3"
    
    # Crear cliente
    key = SupabaseConfig.SUPABASE_ANON_KEY or SupabaseConfig.SUPABASE_SERVICE_ROLE_KEY
    client = create_client(SupabaseConfig.SUPABASE_URL, key)
    
    bucket_name = "portfolio-files"
    
    # Lista de archivos PNG a eliminar
    png_files = [
        f"{user_id}/portfolio_chart.png",
        f"{user_id}/allocation_chart.png",
        f"{user_id}/AAPL_chart.png",
        f"{user_id}/TSLA_chart.png",
        f"{user_id}/MSFT_chart.png",
        f"{user_id}/GOOG_chart.png",
        f"{user_id}/AMZN_chart.png",
        f"{user_id}/PAXG-USD_chart.png",
        f"{user_id}/BTC-USD_chart.png",
        f"{user_id}/NVDA_chart.png",
    ]
    
    print(f"\nBucket: {bucket_name}")
    print(f"Usuario: {user_id}")
    print(f"\nArchivos a eliminar: {len(png_files)}\n")
    
    deleted = 0
    not_found = 0
    errors = 0
    
    for file_path in png_files:
        try:
            # Intentar eliminar
            client.storage.from_(bucket_name).remove([file_path])
            print(f"✓ Eliminado: {file_path}")
            deleted += 1
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "404" in error_msg:
                print(f"⊘ No existe: {file_path}")
                not_found += 1
            else:
                print(f"✗ Error eliminando {file_path}: {e}")
                errors += 1
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"Eliminados:   {deleted}")
    print(f"No existían:  {not_found}")
    print(f"Errores:      {errors}")
    print()
    
    if deleted > 0:
        print("✅ Archivos PNG obsoletos eliminados de Supabase Storage")
        print("\nLos archivos HTML con datos correctos se mantienen:")
        print(f"  - {user_id}/allocation_chart.html (PAXG-USD, BTC-USD, NVDA)")
        print(f"  - {user_id}/portfolio_chart.html")
        print(f"  - {user_id}/portfolio_data.json")
    
    return 0 if errors == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

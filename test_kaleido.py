#!/usr/bin/env python3
"""
Script de prueba para verificar la instalación y funcionamiento de kaleido en Heroku.
Ejecutar con: python test_kaleido.py
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_kaleido_import():
    """Prueba 1: Verificar que kaleido se pueda importar"""
    try:
        import kaleido
        logger.info(f"✅ kaleido importado exitosamente - Versión: {kaleido.__version__}")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando kaleido: {e}")
        return False

def test_plotly_import():
    """Prueba 2: Verificar que plotly se pueda importar"""
    try:
        import plotly
        import plotly.graph_objects as go
        logger.info(f"✅ plotly importado exitosamente - Versión: {plotly.__version__}")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando plotly: {e}")
        return False

def test_png_generation():
    """Prueba 3: Intentar generar un PNG simple"""
    try:
        import plotly.graph_objects as go
        
        # Crear gráfico simple
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
        fig.update_layout(title="Test Chart")
        
        # Intentar generar PNG en memoria
        img_bytes = fig.to_image(format="png", width=800, height=400)
        
        if img_bytes and len(img_bytes) > 0:
            logger.info(f"✅ PNG generado exitosamente ({len(img_bytes)} bytes)")
            return True
        else:
            logger.error("❌ PNG generado pero está vacío")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error generando PNG: {e}")
        return False

def test_write_image():
    """Prueba 4: Intentar escribir imagen a archivo temporal"""
    try:
        import plotly.graph_objects as go
        import tempfile
        import os
        
        # Crear gráfico simple
        fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])
        fig.update_layout(title="Test Chart")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Intentar escribir imagen
            fig.write_image(tmp_path, width=800, height=400)
            
            # Verificar que el archivo existe y tiene contenido
            if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                size = os.path.getsize(tmp_path)
                logger.info(f"✅ Imagen escrita exitosamente ({size} bytes)")
                os.unlink(tmp_path)
                return True
            else:
                logger.error("❌ Archivo creado pero está vacío")
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return False
        except Exception as e:
            logger.error(f"❌ Error escribiendo imagen: {e}")
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en test de write_image: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    logger.info("=" * 70)
    logger.info("VERIFICACIÓN DE KALEIDO PARA HEROKU")
    logger.info("=" * 70)
    
    results = {
        "import_kaleido": test_kaleido_import(),
        "import_plotly": test_plotly_import(),
        "png_generation": test_png_generation(),
        "write_image": test_write_image()
    }
    
    logger.info("\n" + "=" * 70)
    logger.info("RESUMEN DE PRUEBAS")
    logger.info("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:20s}: {status}")
    
    all_passed = all(results.values())
    
    logger.info("=" * 70)
    if all_passed:
        logger.info("✅ TODAS LAS PRUEBAS PASARON - Kaleido está funcionando correctamente")
        return 0
    else:
        logger.error("❌ ALGUNAS PRUEBAS FALLARON - Revisar la instalación de kaleido")
        logger.info("\n💡 Pasos de solución:")
        logger.info("1. Verificar que kaleido==0.2.1 esté en requirements.txt")
        logger.info("2. Agregar buildpack APT: heroku buildpacks:add --index 1 heroku-community/apt")
        logger.info("3. Verificar que Aptfile contenga las dependencias del sistema")
        logger.info("4. Usar stack heroku-22 o superior")
        return 1

if __name__ == "__main__":
    sys.exit(main())

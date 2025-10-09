"""
FastAPI service para Portfolio Manager
Este servicio ejecuta el generador de reportes bajo demanda
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import logging
import asyncio
from datetime import datetime, timedelta

from portfolio_manager import PortfolioManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Portfolio Manager Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia global del Portfolio Manager
portfolio_manager = PortfolioManager()

# Lock para evitar generaciones concurrentes
generation_lock = asyncio.Lock()

# Tracking de última generación
last_generation: dict = {
    "timestamp": None,
    "period": None,
    "in_progress": False,
}


def should_regenerate() -> bool:
    """Determina si se debe regenerar el reporte"""
    if last_generation["in_progress"]:
        return False
    
    if not last_generation["timestamp"]:
        return True
    
    # Regenerar solo si pasaron más de 15 minutos
    last_time = datetime.fromisoformat(last_generation["timestamp"])
    elapsed = datetime.now() - last_time
    return elapsed > timedelta(minutes=15)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Portfolio Manager",
        "timestamp": datetime.now().isoformat(),
        "last_generation": last_generation.get("timestamp"),
        "in_progress": last_generation.get("in_progress"),
    }


@app.post("/process/{user_id}")
async def process_portfolio(user_id: str, period: str = "6mo", force: bool = False):
    """
    Genera el reporte completo del portfolio
    Este endpoint debe ser llamado cada 15 minutos durante horas de mercado
    """
    
    # Si hay una generación en progreso y no es forzada, devolver datos del JSON
    if last_generation["in_progress"] and not force:
        logger.info("Generación en progreso, devolviendo datos existentes")
        try:
            data = portfolio_manager._load_existing_portfolio_data()
            if data:
                return {
                    "status": "success",
                    "message": "Datos del cache (generación en progreso)",
                    "user_id": user_id,
                    "persisted": True,
                    "report": data,
                }
        except Exception as e:
            logger.error(f"Error leyendo JSON existente: {e}")
    
    # Verificar si se debe regenerar
    if not force and not should_regenerate():
        logger.info("Reporte reciente disponible, usando cache")
        try:
            data = portfolio_manager._load_existing_portfolio_data()
            if data:
                return {
                    "status": "success",
                    "message": "Datos del cache (generados recientemente)",
                    "user_id": user_id,
                    "persisted": True,
                    "report": data,
                }
        except Exception as e:
            logger.error(f"Error leyendo JSON existente: {e}")
    
    # Usar lock para evitar generaciones concurrentes
    async with generation_lock:
        # Double-check después de adquirir el lock
        if not force and not should_regenerate():
            logger.info("Reporte ya generado por otro proceso")
            try:
                data = portfolio_manager._load_existing_portfolio_data()
                if data:
                    return {
                        "status": "success",
                        "message": "Datos del cache",
                        "user_id": user_id,
                        "persisted": True,
                        "report": data,
                    }
            except Exception as e:
                logger.error(f"Error leyendo JSON: {e}")
        
        try:
            last_generation["in_progress"] = True
            logger.info(f"🔄 Generando nuevo reporte para user_id={user_id}, period={period}")
            
            # Generar el reporte (ejecutar en thread pool para no bloquear)
            loop = asyncio.get_event_loop()
            report = await loop.run_in_executor(
                None,
                portfolio_manager.generate_full_report,
                period
            )
            
            # Actualizar tracking
            last_generation["timestamp"] = datetime.now().isoformat()
            last_generation["period"] = period
            last_generation["in_progress"] = False
            
            logger.info(f"✅ Reporte generado exitosamente")
            
            return {
                "status": "success",
                "message": "Reporte generado exitosamente",
                "user_id": user_id,
                "persisted": True,
                "report": report,
            }
        
        except Exception as e:
            last_generation["in_progress"] = False
            logger.error(f"❌ Error procesando portfolio: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/summary")
async def get_summary():
    """Obtiene solo el summary del portfolio desde el JSON"""
    try:
        data = portfolio_manager._load_existing_portfolio_data()
        if not data:
            return {
                "status": "no_data",
                "message": "No hay datos disponibles. Ejecute /process primero.",
            }
        
        return {
            "status": "success",
            "summary": data.get("summary"),
            "generated_at": data.get("generated_at"),
            "period": data.get("period"),
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market")
async def get_market():
    """Obtiene solo el market overview desde el JSON"""
    try:
        data = portfolio_manager._load_existing_portfolio_data()
        if not data:
            return {
                "status": "no_data",
                "message": "No hay datos disponibles. Ejecute /process primero.",
            }
        
        return {
            "status": "success",
            "market_overview": data.get("market_overview"),
            "generated_at": data.get("generated_at"),
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo market overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report")
async def get_report():
    """Obtiene el reporte completo desde el JSON"""
    try:
        data = portfolio_manager._load_existing_portfolio_data()
        if not data:
            return {
                "status": "no_data",
                "message": "No hay datos disponibles. Ejecute /process primero.",
            }
        
        return {
            "status": "success",
            "report": data,
        }
    
    except Exception as e:
        logger.error(f"Error obteniendo reporte: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/charts/{chart_name}")
async def get_chart(chart_name: str):
    """Sirve los archivos HTML de los gráficos"""
    try:
        charts_dir = Path(__file__).parent / "charts"
        
        # Mapeo de nombres de gráficos
        chart_files = {
            "portfolio": charts_dir / "portfolio_chart.html",
            "allocation": charts_dir / "allocation_chart.html",
        }
        
        # Si es un símbolo de asset
        if chart_name not in chart_files:
            asset_chart = charts_dir / "assets" / f"{chart_name.upper()}_chart.html"
            if asset_chart.exists():
                return FileResponse(asset_chart, media_type="text/html")
        
        # Gráfico predefinido
        chart_path = chart_files.get(chart_name)
        if not chart_path or not chart_path.exists():
            raise HTTPException(status_code=404, detail=f"Gráfico '{chart_name}' no encontrado")
        
        return FileResponse(chart_path, media_type="text/html")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sirviendo gráfico: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")

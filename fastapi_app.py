"""
Servicio FastAPI del Portfolio Manager
- Entrega datos persistidos (JSON) mediante /report, /summary y /market
- Genera un nuevo reporte sólo bajo demanda usando /process/{user_id}
- Evita ejecuciones concurrentes con un lock asíncrono y respeta un intervalo mínimo
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pytz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import PORTFOLIO_CONFIG, SupabaseConfig
from portfolio_manager import PortfolioManager

logging.basicConfig(level=os.getenv("PORTFOLIO_LOG_LEVEL", "INFO"))
logger = logging.getLogger("portfolio_manager.service")

# --- Configuración general ---
DEFAULT_PERIOD = os.getenv("PORTFOLIO_MANAGER_DEFAULT_PERIOD", "6mo")
MARKET_TZ = pytz.timezone("America/New_York")
REFRESH_INTERVAL = timedelta(minutes=15)

# --- Instancias globales ---
portfolio_manager = PortfolioManager()
generation_lock = asyncio.Lock()
last_generation_state: Dict[str, Optional[object]] = {
    "timestamp": None,  # datetime
    "period": None,
    "in_progress": False,
}
scheduler = AsyncIOScheduler(timezone=MARKET_TZ)


# --- Modelos ---


class ProcessRequest(BaseModel):
    period: Optional[str] = Field(default=None, description="Periodo para yfinance (ej. '6mo')")
    force: bool = Field(default=False, description="Forzar generación sin validaciones adicionales")
    symbols: Optional[List[str]] = Field(default=None, description="Símbolos para validar horario de mercado")


# --- Utilidades internas ---


def _update_last_generation(dt: Optional[datetime], period: Optional[str]) -> None:
    last_generation_state["timestamp"] = dt
    last_generation_state["period"] = period


def _parse_generated_at(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo:
            parsed = parsed.astimezone(pytz.UTC).replace(tzinfo=None)
        return parsed
    except (ValueError, TypeError):
        return None


def initialize_last_generation() -> None:
    report = portfolio_manager._load_existing_portfolio_data()
    if not isinstance(report, dict):
        return
    generated_at = _parse_generated_at(report.get("generated_at"))
    _update_last_generation(generated_at, report.get("period", DEFAULT_PERIOD))


def _load_report_from_disk() -> Optional[Dict[str, object]]:
    data = portfolio_manager._load_existing_portfolio_data()
    if not data:
        return None
    generated_at = _parse_generated_at(data.get("generated_at"))
    _update_last_generation(generated_at, data.get("period"))
    return data


def _should_regenerate(requested_period: str) -> bool:
    if last_generation_state["in_progress"]:
        return False
    last_dt: Optional[datetime] = last_generation_state.get("timestamp")  # type: ignore[assignment]
    last_period = last_generation_state.get("period")
    if not last_dt:
        return True  # nunca se ha generado
    if last_period and last_period != requested_period:
        return True
    return datetime.utcnow() - last_dt > REFRESH_INTERVAL


def _is_market_open(now: Optional[datetime] = None) -> bool:
    current = now.astimezone(MARKET_TZ) if now else datetime.now(MARKET_TZ)
    if current.weekday() >= 5:  # sábado o domingo
        return False
    open_time = current.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = current.replace(hour=16, minute=0, second=0, microsecond=0)
    return open_time <= current <= close_time


async def maybe_generate(period: str = DEFAULT_PERIOD, *, force: bool = False) -> Optional[Dict[str, object]]:
    if not force and not _is_market_open():
        logger.debug("Mercado cerrado. Se omite la generación automática.")
        return None

    if not force and not _should_regenerate(period):
        return None

    async with generation_lock:
        if not force and not _should_regenerate(period):
            return None

        try:
            last_generation_state["in_progress"] = True
            logger.info("🔄 Generando nuevo reporte (period=%s, force=%s)", period, force)
            loop = asyncio.get_running_loop()
            report = await loop.run_in_executor(None, portfolio_manager.generate_full_report, period)
            generated_at = _parse_generated_at(report.get("generated_at") if isinstance(report, dict) else None)
            _update_last_generation(generated_at or datetime.utcnow(), period)
            return report
        finally:
            last_generation_state["in_progress"] = False


# --- FastAPI ---

app = FastAPI(title="Portfolio Manager Service", version="3.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("PORTFOLIO_MANAGER_CORS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    if SupabaseConfig.is_configured():
        logger.info(
            "Supabase configurado. Bucket=%s, prefix_json=%s, prefix_charts=%s",
            SupabaseConfig.SUPABASE_BUCKET_NAME,
            SupabaseConfig.SUPABASE_BASE_PREFIX,
            SupabaseConfig.SUPABASE_BASE_PREFIX2,
        )
    else:
        logger.warning(
            "Supabase no está configurado o está deshabilitado; se usará almacenamiento local como fallback.")

    initialize_last_generation()
    # Si no hay datos persistidos o es necesario, generar uno inicial (fuera de horario se salta)
    try:
        await maybe_generate(force=False)
    except Exception:
        logger.exception("Error generando reporte inicial")
    trigger = CronTrigger(
        day_of_week="mon-fri",
        hour="9-16",
        minute="0,15,30,45",
    )
    scheduler.add_job(
        maybe_generate,
        trigger=trigger,
        id="portfolio_auto_generation",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


@app.get("/health")
async def health() -> Dict[str, object]:
    ts = last_generation_state.get("timestamp")
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "last_generation": ts.isoformat() if isinstance(ts, datetime) else None,
        "period": last_generation_state.get("period"),
        "in_progress": last_generation_state.get("in_progress"),
        "supabase": {
            "configured": SupabaseConfig.is_configured(),
            "bucket": SupabaseConfig.SUPABASE_BUCKET_NAME,
            "data_prefix": SupabaseConfig.SUPABASE_BASE_PREFIX,
            "charts_prefix": SupabaseConfig.SUPABASE_BASE_PREFIX2,
        },
    }


@app.get("/report")
async def get_report() -> Dict[str, object]:
    report = _load_report_from_disk()
    if not report:
        return {
            "status": "no_data",
            "message": "No existen datos persistidos aún.",
            "report": None,
        }
    return {
        "status": "success",
        "persisted": True,
        "report": report,
    }


@app.get("/summary")
async def get_summary() -> Dict[str, object]:
    report = _load_report_from_disk()
    summary = report["summary"] if isinstance(report, dict) and "summary" in report else None
    generated_at = report["generated_at"] if isinstance(report, dict) and "generated_at" in report else None
    return {
        "status": "success" if summary else "no_data",
        "persisted": bool(summary),
        "summary": summary,
        "generated_at": generated_at,
    }


@app.get("/market")
async def get_market() -> Dict[str, object]:
    report = _load_report_from_disk()
    market = report["market_overview"] if isinstance(report, dict) and "market_overview" in report else None
    if not market:
        return {
            "status": "no_data",
            "message": "No hay datos de mercado disponibles. Ejecuta /process para generarlos.",
            "market_overview": None,
        }
    generated_at = report["generated_at"] if isinstance(report, dict) and "generated_at" in report else None
    return {
        "status": "success",
        "persisted": True,
        "generated_at": generated_at,
        "market_overview": market,
    }


@app.post("/process/{user_id}")
async def process_portfolio(user_id: str, request: ProcessRequest) -> Dict[str, object]:
    period = request.period or DEFAULT_PERIOD
    symbols = request.symbols or [asset.get("symbol", "").upper() for asset in PORTFOLIO_CONFIG.get("assets", []) if asset.get("symbol")]

    # Si hay generación en curso y no es forzada, devolver cache
    if last_generation_state["in_progress"] and not request.force:
        report = _load_report_from_disk()
        if report:
            return {
                "status": "success",
                "message": "Generación en curso. Datos desde JSON.",
                "user_id": user_id,
                "persisted": True,
                "report": report,
            }

    if not request.force and not _should_regenerate(period):
        report = _load_report_from_disk()
        if report:
            return {
                "status": "success",
                "message": "Datos recientes desde JSON.",
                "user_id": user_id,
                "persisted": True,
                "report": report,
            }

    if not request.force and symbols and not any(symbol.endswith("-USD") for symbol in symbols):
        if not _is_market_open():
            return {
                "status": "skipped",
                "user_id": user_id,
                "market_open": False,
                "message": "Mercado cerrado. No se genera un nuevo reporte.",
            }

    async with generation_lock:
        # Doble verificación antes de generar
        if not request.force and not _should_regenerate(period):
            report = _load_report_from_disk()
            if report:
                return {
                    "status": "success",
                    "message": "Datos recientes desde JSON.",
                    "user_id": user_id,
                    "persisted": True,
                    "report": report,
                }

        try:
            last_generation_state["in_progress"] = True
            loop = asyncio.get_running_loop()
            report = await loop.run_in_executor(None, portfolio_manager.generate_full_report, period)
            generated_at = report.get("generated_at") if isinstance(report, dict) else None
            dt = None
            if isinstance(generated_at, str):
                try:
                    dt = datetime.fromisoformat(generated_at)
                except ValueError:
                    dt = datetime.utcnow()
            else:
                dt = datetime.utcnow()
            _update_last_generation(dt, period)
            return {
                "status": "success",
                "user_id": user_id,
                "persisted": True,
                "period": period,
                "message": "Reporte generado exitosamente",
                "report": report,
            }
        except Exception as exc:
            logger.exception("Error generando reporte: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))
        finally:
            last_generation_state["in_progress"] = False


@app.get("/charts/{chart_name}", response_class=FileResponse)
async def get_chart(chart_name: str) -> FileResponse:
    charts_dir = Path(__file__).parent / "charts"

    mapping = {
        "portfolio": charts_dir / "portfolio_chart.html",
        "allocation": charts_dir / "allocation_chart.html",
    }

    if chart_name in mapping:
        target = mapping[chart_name]
    else:
        target = charts_dir / "assets" / f"{chart_name.upper()}_chart.html"

    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Gráfico '{chart_name}' no encontrado")

    return FileResponse(target, media_type="text/html")


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "service": "portfolio-manager",
        "mode": "on-demand",
        "default_period": DEFAULT_PERIOD,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fastapi_app:app",
        host=os.getenv("PORTFOLIO_MANAGER_HOST", "0.0.0.0"),
        port=int(os.getenv("PORTFOLIO_MANAGER_PORT", "9000")),
        reload=os.getenv("PORTFOLIO_MANAGER_RELOAD", "false").lower() == "true",
    )

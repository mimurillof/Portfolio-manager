"""Servicio FastAPI para el Portfolio Manager bajo demanda.

El servicio genera reportes únicamente cuando se invoca el endpoint
``POST /process/{user_id}``, evitando ejecuciones constantes. Incluye verificación
de horario de mercado (NYSE) y un bypass automático para símbolos considerados
criptoactivos.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional

import pytz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from config import PORTFOLIO_CONFIG
from portfolio_manager import PortfolioManager
from api_integration import get_chart_html_for_api

logger = logging.getLogger("portfolio_manager.service")
logging.basicConfig(level=os.getenv("PORTFOLIO_LOG_LEVEL", "INFO"))

DEFAULT_PERIOD = os.getenv("PORTFOLIO_MANAGER_DEFAULT_PERIOD", "6mo")
TIMEZONE_NY = pytz.timezone("America/New_York")


class ProcessRequest(BaseModel):
    period: Optional[str] = Field(default=None, description="Periodo de análisis para yfinance")
    force: bool = Field(default=False, description="Ignorar validaciones de horario de mercado")
    symbols: Optional[List[str]] = Field(
        default=None,
        description="Lista de símbolos a validar. Si se omite, se usan los del portafolio por defecto.",
    )


def get_default_symbols() -> List[str]:
    return [asset.get("symbol", "").upper() for asset in PORTFOLIO_CONFIG.get("assets", []) if asset.get("symbol")]


def is_crypto_symbol(symbol: str) -> bool:
    symbol = symbol.upper()
    return symbol.endswith("-USD") or symbol.startswith("BTC") or symbol.startswith("ETH") or "CRYPTO" in symbol


def market_is_open(now: Optional[datetime] = None) -> bool:
    current = now.astimezone(TIMEZONE_NY) if now else datetime.now(TIMEZONE_NY)
    if current.weekday() >= 5:  # Saturday/Sunday
        return False
    open_time = current.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = current.replace(hour=16, minute=0, second=0, microsecond=0)
    return open_time <= current <= close_time


def next_market_window(now: Optional[datetime] = None) -> Dict[str, str]:
    current = now.astimezone(TIMEZONE_NY) if now else datetime.now(TIMEZONE_NY)
    next_open = current.replace(hour=9, minute=30, second=0, microsecond=0)
    if current.time() >= time(16, 0) or current.weekday() >= 4:
        days_ahead = 1
        if current.weekday() == 4:  # Friday -> Monday
            days_ahead = 3
        elif current.weekday() == 5:  # Saturday -> Monday
            days_ahead = 2
        next_open = (current + timedelta(days=days_ahead)).replace(hour=9, minute=30, second=0, microsecond=0)
    elif current.time() < time(9, 30):
        next_open = current.replace(hour=9, minute=30, second=0, microsecond=0)
    return {
        "next_open_est": next_open.isoformat(),
        "timezone": "America/New_York",
    }


async def generate_report(period: str) -> Dict[str, object]:
    manager = PortfolioManager()
    loop = asyncio.get_running_loop()
    report = await loop.run_in_executor(None, manager.generate_full_report, period)
    return report


app = FastAPI(
    title="Portfolio Manager Service",
    version="2.0.0",
    description="Servicio under-demand para cálculos de portafolio",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("PORTFOLIO_MANAGER_CORS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/process/{user_id}")
async def process_portfolio(user_id: str, request: ProcessRequest) -> Dict[str, object]:
    period = request.period or DEFAULT_PERIOD
    symbols = request.symbols or get_default_symbols()
    market_open = True
    message = ""

    if not request.force and symbols and not any(is_crypto_symbol(symbol) for symbol in symbols):
        market_open = market_is_open()
        if not market_open:
            message = "Mercado cerrado. Se omite la actualización hasta la próxima ventana hábil."
            response: Dict[str, object] = {
                "status": "skipped",
                "user_id": user_id,
                "market_open": False,
                "message": message,
            }
            response.update(next_market_window())
            return response

    report = await generate_report(period)
    last_updated = datetime.utcnow().isoformat()

    return {
        "status": "success",
        "user_id": user_id,
        "period": period,
        "market_open": market_open,
        "message": "Reporte generado exitosamente",
        "last_updated": last_updated,
        "report": report,
    }


@app.get("/charts/{chart_name}", response_class=HTMLResponse)
async def get_chart(chart_name: str) -> HTMLResponse:
    html = await asyncio.get_running_loop().run_in_executor(None, get_chart_html_for_api, chart_name)
    if not html:
        raise HTTPException(status_code=404, detail=f"No se encontró el gráfico '{chart_name}'")
    return HTMLResponse(content=html)


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

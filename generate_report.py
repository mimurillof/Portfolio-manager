#!/usr/bin/env python3
"""Worker para generar el reporte del Portfolio de forma recurrente.

Permite ejecutar el proceso una sola vez (modo CLI) o como worker
en Heroku ejecutándose en bucle cada cierto intervalo de minutos.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import datetime, time as time_cls
from pathlib import Path
from typing import Optional, Set

import pytz

from portfolio_manager import PortfolioManager


LOGGER = logging.getLogger("portfolio.generate_report")

DEFAULT_PERIOD = os.getenv("PORTFOLIO_DEFAULT_PERIOD", "6mo")
DEFAULT_INTERVAL_MINUTES = int(os.getenv("PORTFOLIO_WORKER_INTERVAL_MINUTES", "15"))
TRADING_WINDOW_RAW = os.getenv("PORTFOLIO_TRADING_WINDOW", "09:30-16:00")
TRADING_TZ_NAME = os.getenv("PORTFOLIO_TRADING_TZ", "America/New_York")
TRADING_DAYS_RAW = os.getenv("PORTFOLIO_TRADING_DAYS", "0-4")


def _parse_trading_window(window: str) -> Optional[tuple[time_cls, time_cls]]:
    window = (window or "").strip()
    if not window or window.lower() == "siempre" or window.lower() == "always":
        return None

    try:
        start_str, end_str = [chunk.strip() for chunk in window.split("-", 1)]
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()
        return start_time, end_time
    except Exception:  # pylint: disable=broad-except
        LOGGER.warning(
            "No se pudo interpretar PORTFOLIO_TRADING_WINDOW='%s'. Se ejecutará siempre.",
            window,
        )
        return None


def _parse_trading_days(raw_days: str) -> Optional[Set[int]]:
    raw_days = (raw_days or "").strip()
    if not raw_days:
        return None

    days: Set[int] = set()
    for chunk in raw_days.split(","):
        part = chunk.strip()
        if not part:
            continue
        if "-" in part:
            try:
                start_str, end_str = part.split("-", 1)
                start = int(start_str)
                end = int(end_str)
                if start > end:
                    start, end = end, start
                days.update(range(start, end + 1))
            except ValueError:
                LOGGER.warning("Rango de días inválido en PORTFOLIO_TRADING_DAYS: '%s'", part)
        else:
            try:
                days.add(int(part))
            except ValueError:
                LOGGER.warning("Día inválido en PORTFOLIO_TRADING_DAYS: '%s'", part)
    if not days:
        return None
    invalid = [d for d in days if d < 0 or d > 6]
    if invalid:
        LOGGER.warning("Días fuera de rango (0-6) en PORTFOLIO_TRADING_DAYS: %s", invalid)
        days = {d for d in days if 0 <= d <= 6}
    return days or None


TRADING_WINDOW = _parse_trading_window(TRADING_WINDOW_RAW)
TRADING_DAYS = _parse_trading_days(TRADING_DAYS_RAW)
try:
    TRADING_TZ = pytz.timezone(TRADING_TZ_NAME)
except Exception:  # pylint: disable=broad-except
    LOGGER.warning("Zona horaria inválida '%s'; se usará UTC.", TRADING_TZ_NAME)
    TRADING_TZ = pytz.UTC


def _configure_logging() -> None:
    """Configura logging básico si aún no está configurado."""
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )


def run_report(period: str, emit_console: bool = True) -> bool:
    """Ejecuta la generación del reporte para el periodo indicado."""
    if emit_console:
        print("=" * 80)
        print("📊 GENERADOR DE REPORTE DE PORTFOLIO CON WEB SCRAPING")
        print("=" * 80)
        print(f"\n🕐 Periodo seleccionado: {period}")
        print("\n🚀 Iniciando generación del reporte...")
        print("   - Obteniendo datos de yfinance para el portfolio")
        print("   - Scrapeando Yahoo Finance para market movers")
        print("   - Enriqueciendo datos con logos y métricas")
        print("   - Generando gráficos de performance")
        print("   - Guardando todo en portfolio_data.json\n")

    try:
        manager = PortfolioManager()
        report = manager.generate_full_report(period=period)

        summary = report.get("summary", {})
        market_overview = report.get("market_overview", {})
        data_file = Path(__file__).parent / "data" / "portfolio_data.json"

        LOGGER.info(
            "Reporte generado (periodo=%s, valor=%.2f, cambio=%.2f%%)",
            period,
            summary.get("total_value", 0.0),
            summary.get("total_change_percent", 0.0),
        )

        if emit_console:
            print("\n" + "=" * 80)
            print("✅ REPORTE GENERADO EXITOSAMENTE")
            print("=" * 80)
            print(f"\n💰 Valor Total: ${summary.get('total_value', 0):,.2f}")
            print(f"📈 Cambio: {summary.get('total_change_percent', 0):+.2f}%")
            print("\n📊 Market Overview:")
            for section, items in market_overview.items():
                if isinstance(items, list):
                    print(f"   • {section}: {len(items)} elementos")
            print(f"\n💾 Datos guardados en: {data_file}")
            print("\n🎯 Próximos pasos:")
            print("   1. Iniciar backend: uvicorn mi-proyecto-backend.main:app --reload")
            print("   2. Iniciar frontend: npm run dev")
            print("   3. Verificar el componente Watchlist en el Dashboard")
            print("\n" + "=" * 80)

        return True
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.exception("Error generando el reporte (periodo=%s)", period)
        if emit_console:
            print(f"\n❌ ERROR: {exc}")
            import traceback  # local import para mantener trazas en CLI

            traceback.print_exc()
        return False


def _within_trading_window(reference: Optional[datetime] = None) -> bool:
    if TRADING_WINDOW is None and TRADING_DAYS is None:
        return True

    now = reference.astimezone(TRADING_TZ) if reference else datetime.now(TRADING_TZ)

    if TRADING_DAYS is not None and now.weekday() not in TRADING_DAYS:
        return False

    if TRADING_WINDOW is None:
        return True

    start, end = TRADING_WINDOW
    current_time = now.time()

    if start <= end:
        return start <= current_time <= end
    # Ventana que cruza medianoche (p.ej., 22:00-02:00)
    return current_time >= start or current_time <= end


def _sleep_with_heartbeat(target_monotonic: float) -> None:
    """Duerme en tramos cortos para permitir logs de vida y señales."""
    heartbeat = int(os.getenv("PORTFOLIO_WORKER_HEARTBEAT_SECONDS", "30"))
    heartbeat = max(5, min(heartbeat, 300))

    while True:
        remaining = target_monotonic - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(heartbeat, remaining))
        LOGGER.debug("Worker en espera; faltan %.1f segundos para la próxima ejecución", max(0.0, remaining - heartbeat))


def run_worker(period: str, interval_minutes: int, run_immediately: bool) -> None:
    """Configura y mantiene el worker en ejecución."""
    if interval_minutes <= 0:
        raise ValueError("Intervalo inválido: debe ser mayor a 0 minutos")

    LOGGER.info(
        "Worker configurado (periodo=%s, intervalo=%s minutos, run_immediately=%s)",
        period,
        interval_minutes,
        run_immediately,
    )

    interval_seconds = interval_minutes * 60
    LOGGER.info(
        "Ventana operativa: %s | Días: %s | Zona horaria: %s",
        TRADING_WINDOW_RAW or "siempre",
        TRADING_DAYS_RAW or "todos",
        TRADING_TZ.zone,
    )

    if run_immediately:
        LOGGER.info("Ejecutando generación inicial antes del loop")
        if _within_trading_window():
            run_report(period, emit_console=False)
        else:
            LOGGER.info("Fuera del horario configurado; se omite corrida inicial")

    next_run = time.monotonic() + interval_seconds
    LOGGER.info("Worker iniciado; siguiente ejecución en %s minutos", interval_minutes)

    try:
        while True:
            _sleep_with_heartbeat(next_run)
            should_run = _within_trading_window()
            if should_run:
                LOGGER.info("Iniciando ejecución programada del reporte")
                run_report(period, emit_console=False)
            else:
                LOGGER.info("Fuera del horario configurado; se omite la ejecución programada")
            next_run = time.monotonic() + interval_seconds
    except KeyboardInterrupt:  # pragma: no cover - interacción manual
        LOGGER.info("Worker detenido manualmente")


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Genera el reporte del Portfolio una vez o como worker recurrente.",
    )
    parser.add_argument(
        "period",
        nargs="?",
        default=DEFAULT_PERIOD,
        help="Periodo para el cálculo (por defecto: %(default)s)",
    )
    parser.add_argument(
        "--worker",
        action="store_true",
        help="Ejecuta el script como worker en bucle continuo.",
    )
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=DEFAULT_INTERVAL_MINUTES,
        help="Minutos entre ejecuciones en modo worker (por defecto: %(default)s)",
    )
    parser.add_argument(
        "--no-initial-run",
        action="store_true",
        help="Evita ejecutar una corrida inmediata al iniciar el worker.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Oculta la salida formateada en consola (solo logs).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada principal."""
    _configure_logging()
    args = parse_args(argv or sys.argv[1:])

    if args.worker:
        try:
            run_worker(
                period=args.period,
                interval_minutes=args.interval_minutes,
                run_immediately=not args.no_initial_run,
            )
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.exception("Fallo crítico en el worker")
            return 1
        return 0

    success = run_report(args.period, emit_console=not args.quiet)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())


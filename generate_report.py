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
from pathlib import Path
from typing import Any

try:
    import schedule as schedule_module
except ImportError:  # pragma: no cover - handled en tiempo de ejecución al iniciar worker
    schedule_module = None

from portfolio_manager import PortfolioManager


LOGGER = logging.getLogger("portfolio.generate_report")

DEFAULT_PERIOD = os.getenv("PORTFOLIO_DEFAULT_PERIOD", "6mo")
DEFAULT_INTERVAL_MINUTES = int(os.getenv("PORTFOLIO_WORKER_INTERVAL_MINUTES", "15"))


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


def _schedule_job(schedule_api: Any) -> None:
    """Ejecuta el loop de schedule hasta que el proceso sea detenido."""
    LOGGER.info("Iniciando loop del worker de generación de reportes")
    try:
        while True:
            schedule_api.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:  # pragma: no cover - interacción manual
        LOGGER.info("Worker detenido manualmente")


def run_worker(period: str, interval_minutes: int, run_immediately: bool) -> None:
    """Configura y mantiene el worker en ejecución."""
    if schedule_module is None:
        raise RuntimeError(
            "La librería 'schedule' es requerida en modo worker. Asegúrate de "
            "agregarla a requirements.txt e instalarla antes de desplegar."
        )

    if interval_minutes <= 0:
        raise ValueError("Intervalo inválido: debe ser mayor a 0 minutos")

    LOGGER.info(
        "Worker configurado (periodo=%s, intervalo=%s minutos, run_immediately=%s)",
        period,
        interval_minutes,
        run_immediately,
    )

    if run_immediately:
        LOGGER.info("Ejecutando generación inicial antes del schedule")
        run_report(period, emit_console=False)

    schedule_module.clear()
    schedule_module.every(interval_minutes).minutes.do(run_report, period, False)
    _schedule_job(schedule_module)


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


"""Validación ligera para los gráficos HTML generados.

Este script crea un gráfico de ejemplo usando ``ChartGenerator.create_asset_chart``
y verifica que el HTML resultante incluya los elementos interactivos clave
(botones de frecuencia y relleno de área). No requiere acceso a internet.

Ejecución desde la raíz del proyecto:

```
python "Portfolio manager/tests/validate_chart_html.py"
```
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

import sys

CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from chart_generator import ChartGenerator  # type: ignore  # pylint: disable=import-error
from config import CHART_CONFIG  # type: ignore  # pylint: disable=import-error


def _build_sample_frames() -> Dict[str, pd.DataFrame]:
    """Crea dataframes sintéticos para las diferentes frecuencias."""
    intraday_index = pd.date_range("2025-01-01 09:30", periods=64, freq="15min")
    intraday_close = pd.Series(
        100 + np.linspace(0, 12.6, num=len(intraday_index)),
        index=intraday_index,
        name="Close",
    )
    intraday_df = intraday_close.to_frame()

    daily_index = pd.date_range("2024-07-01", periods=180, freq="1D")
    daily_close = pd.Series(
        90 + np.linspace(0, 40, num=len(daily_index)),
        index=daily_index,
        name="Close",
    )
    daily_df = daily_close.to_frame()

    return {"intraday": intraday_df, "daily": daily_df}


def _generate_sample_chart(output_path: Path) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = _build_sample_frames()

    generator = ChartGenerator(CHART_CONFIG)
    generator.create_asset_chart(
        symbol="TEST",
        intraday_data=frames["intraday"],
        output_html=output_path,
        output_png=None,
        daily_data=frames["daily"],
        intraday_interval="15m",
    )

    return output_path.read_text(encoding="utf-8")


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    html_path = output_dir / "test_asset_chart.html"

    html_content = _generate_sample_chart(html_path)

    checks = {
        "contiene_updatemenus": "updatemenus" in html_content,
        "contiene_boton_intradia": "15 minutos" in html_content,
        "contiene_traza_hist6m": "Histórico 6M" in html_content,
        "usa_relleno_area": "tozeroy" in html_content,
    }

    failed = [name for name, ok in checks.items() if not ok]

    if failed:
        print("Validación fallida. Revisar los siguientes elementos:")
        for name in failed:
            print(f"  - {name}")
        raise SystemExit(1)

    print("Validación completada correctamente. El HTML incluye interactividad y relleno de área.")
    print(f"Archivo de muestra: {html_path}")


if __name__ == "__main__":
    main()

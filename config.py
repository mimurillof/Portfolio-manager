"""
Configuración para el Portfolio Manager
"""
import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

# Directorios
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHARTS_DIR = BASE_DIR / "charts"
OUTPUT_DIR = BASE_DIR / "output"

# Crear directorios si no existen (se mantienen como fallback local)
for directory in [DATA_DIR, CHARTS_DIR, OUTPUT_DIR]:
    directory.mkdir(exist_ok=True)


if load_dotenv:
    load_dotenv()  # Carga variables desde .env si está disponible


class SupabaseConfig:
    """Configuración centralizada para Supabase."""

    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_ANON_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_BUCKET_NAME: str = os.getenv("SUPABASE_BUCKET_NAME", "portfolio-files")
    SUPABASE_BASE_PREFIX: str = os.getenv("SUPABASE_BASE_PREFIX", "portfolio-data")
    SUPABASE_BASE_PREFIX2: str = (
        os.getenv("SUPABASE_BASE_PREFIX2")
        or os.getenv("SUPABASE_BASE_PREFIX_2")
        or os.getenv("SUPABASE_BASE_PREFIX", "Graficos")
    )
    SUPABASE_PORTFOLIO_FILENAME: str = os.getenv("SUPABASE_PORTFOLIO_FILENAME", "portfolio_data.json")
    ENABLE_SUPABASE_UPLOAD: bool = os.getenv("ENABLE_SUPABASE_UPLOAD", "true").lower() == "true"

    @classmethod
    def get_supabase_key(cls) -> str:
        return cls.SUPABASE_SERVICE_ROLE_KEY or cls.SUPABASE_ANON_KEY or ""

    @classmethod
    def is_configured(cls) -> bool:
        return bool(cls.SUPABASE_URL and cls.get_supabase_key()) and cls.ENABLE_SUPABASE_UPLOAD

    @classmethod
    def portfolio_json_path(cls) -> str:
        prefix = (cls.SUPABASE_BASE_PREFIX or "").strip("/")
        if prefix:
            return f"{prefix}/{cls.SUPABASE_PORTFOLIO_FILENAME}".strip("/")
        return cls.SUPABASE_PORTFOLIO_FILENAME

    @classmethod
    def charts_prefix(cls) -> str:
        return (cls.SUPABASE_BASE_PREFIX2 or "Graficos").strip("/")

    @classmethod
    def build_chart_path(cls, relative_path: str) -> str:
        relative_clean = relative_path.strip("/")
        prefix = cls.charts_prefix()
        if prefix:
            return f"{prefix}/{relative_clean}".strip("/")
        return relative_clean

    @classmethod
    def remote_chart_path_for(cls, local_path: Path) -> str:
        try:
            relative = local_path.relative_to(CHARTS_DIR)
        except ValueError:
            relative = local_path.name

        if isinstance(relative, Path):
            relative_str = relative.as_posix()
        else:
            relative_str = str(relative)

        return cls.build_chart_path(relative_str)


# Portfolio configuration
PORTFOLIO_CONFIG = {
    "assets": [
        {"symbol": "AAPL", "units": 10, "name": "Apple"},
        {"symbol": "TSLA", "units": 20, "name": "Tesla"},
        {"symbol": "MSFT", "units": 15, "name": "Microsoft"},
        {"symbol": "GOOG", "units": 5, "name": "Google"},
        {"symbol": "AMZN", "units": 8, "name": "Amazon"},
    ]
}

# Watchlist configuration (activos del mercado en general)
WATCHLIST = [
    {"symbol": "SPOT", "name": "Spotify", "exchange": "NYSE"},
    {"symbol": "AMZN", "name": "Amazon", "exchange": "NYSE"},
    {"symbol": "MSFT", "name": "Microsoft", "exchange": "NASDAQ"},
    {"symbol": "DIS", "name": "Disney", "exchange": "NYSE"},
    {"symbol": "NVDA", "name": "NVIDIA", "exchange": "NASDAQ"},
    {"symbol": "META", "name": "Meta", "exchange": "NASDAQ"},
    {"symbol": "JPM", "name": "JPMorgan", "exchange": "NYSE"},
]

# Periodos de tiempo disponibles
TIME_PERIODS = {
    "1D": "1d",
    "1W": "1wk",
    "1M": "1mo",
    "6M": "6mo",
    "1Y": "1y",
}

# Configuración de gráficos
CHART_CONFIG = {
    "width": 1566,
    "height": 365,
    "template": "plotly_white",
    "colors": {
        "positive": "#10b981",  # green
        "negative": "#ef4444",  # red
        "neutral": "#3b82f6",   # blue
        "background": "#ffffff",
        "text": "#1f2937",
    },
    "enable_png_export": os.getenv("PORTFOLIO_ENABLE_PNG", "true").lower() == "true",
}

# Archivos de salida (fallback local)
OUTPUT_FILES = {
    "portfolio_data": DATA_DIR / "portfolio_data.json",
    "market_data": DATA_DIR / "market_data.json",
    "portfolio_chart_html": CHARTS_DIR / "portfolio_chart.html",
    "portfolio_chart_png": CHARTS_DIR / "portfolio_chart.png",
    "assets_charts_dir": CHARTS_DIR / "assets",
}

# Crear subdirectorio para gráficos de assets
(CHARTS_DIR / "assets").mkdir(exist_ok=True)

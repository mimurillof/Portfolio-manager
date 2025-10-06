"""
Configuración para el Portfolio Manager
"""
import os
from pathlib import Path

# Directorios
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHARTS_DIR = BASE_DIR / "charts"
OUTPUT_DIR = BASE_DIR / "output"

# Crear directorios si no existen
for directory in [DATA_DIR, CHARTS_DIR, OUTPUT_DIR]:
    directory.mkdir(exist_ok=True)

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
    }
}

# Archivos de salida
OUTPUT_FILES = {
    "portfolio_data": DATA_DIR / "portfolio_data.json",
    "market_data": DATA_DIR / "market_data.json",
    "portfolio_chart_html": CHARTS_DIR / "portfolio_chart.html",
    "portfolio_chart_png": CHARTS_DIR / "portfolio_chart.png",
    "assets_charts_dir": CHARTS_DIR / "assets",
}

# Crear subdirectorio para gráficos de assets
(CHARTS_DIR / "assets").mkdir(exist_ok=True)

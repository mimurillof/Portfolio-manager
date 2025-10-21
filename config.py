"""
Configuración para el Portfolio Manager
"""
import os
import logging
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
    def portfolio_json_path(cls, user_id: Optional[str] = None) -> str:
        """
        Genera la ruta del archivo JSON del portfolio.
        
        Args:
            user_id: UUID del usuario. Si se proporciona, usa estructura {user_id}/portfolio_data.json
                    Si no se proporciona, usa el prefijo legacy SUPABASE_BASE_PREFIX
        
        Returns:
            Ruta relativa en el bucket
        """
        if user_id:
            # Nueva estructura plana: {user_id}/portfolio_data.json
            return f"{user_id}/{cls.SUPABASE_PORTFOLIO_FILENAME}".strip("/")
        
        # Fallback legacy para compatibilidad
        prefix = (cls.SUPABASE_BASE_PREFIX or "").strip("/")
        if prefix:
            return f"{prefix}/{cls.SUPABASE_PORTFOLIO_FILENAME}".strip("/")
        return cls.SUPABASE_PORTFOLIO_FILENAME

    @classmethod
    def charts_prefix(cls, user_id: Optional[str] = None) -> str:
        """
        Obtiene el prefijo para gráficos.
        
        Args:
            user_id: UUID del usuario. Si se proporciona, usa estructura {user_id}/
        
        Returns:
            Prefijo para gráficos (sin subcarpetas adicionales)
        """
        if user_id:
            # Estructura plana: archivos directamente en {user_id}/
            return f"{user_id}"
        
        # Fallback legacy
        return (cls.SUPABASE_BASE_PREFIX2 or "Graficos").strip("/")

    @classmethod
    def build_chart_path(cls, relative_path: str, user_id: Optional[str] = None) -> str:
        """
        Construye la ruta completa para un gráfico.
        
        Args:
            relative_path: Ruta relativa del gráfico
            user_id: UUID del usuario
        
        Returns:
            Ruta completa en el bucket (plana, sin subdirectorios)
        """
        # Extraer solo el nombre del archivo, sin subdirectorios
        from pathlib import Path as PathLib
        filename = PathLib(relative_path).name
        
        prefix = cls.charts_prefix(user_id)
        if prefix:
            return f"{prefix}/{filename}".strip("/")
        return filename

    @classmethod
    def sanitize_filename_for_storage(cls, filename: str) -> str:
        """
        Sanitiza un nombre de archivo para ser compatible con Supabase Storage.
        
        Supabase Storage tiene restricciones sobre caracteres especiales en las claves.
        Esta función reemplaza caracteres problemáticos por alternativas seguras.
        
        Args:
            filename: Nombre de archivo original (ej: "^SPX_chart.html")
        
        Returns:
            Nombre de archivo sanitizado (ej: "_CARET_SPX_chart.html")
        
        Examples:
            >>> SupabaseConfig.sanitize_filename_for_storage("^SPX_chart.html")
            "_CARET_SPX_chart.html"
            >>> SupabaseConfig.sanitize_filename_for_storage("BTC-USD_chart.html")
            "BTC-USD_chart.html"
        """
        # Mapeo de caracteres problemáticos a reemplazos seguros
        replacements = {
            '^': '_CARET_',     # Índices como ^SPX, ^GSPC
            '<': '_LT_',        # Menor que
            '>': '_GT_',        # Mayor que
            ':': '_COLON_',     # Dos puntos
            '"': '_QUOTE_',     # Comillas dobles
            '\\': '_BSLASH_',   # Barra invertida
            '|': '_PIPE_',      # Pipe
            '?': '_QMARK_',     # Signo de interrogación
            '*': '_STAR_',      # Asterisco
        }
        
        sanitized = filename
        for char, replacement in replacements.items():
            sanitized = sanitized.replace(char, replacement)
        
        return sanitized
    
    @classmethod
    def remote_chart_path_for(cls, local_path: Path, user_id: Optional[str] = None) -> str:
        """
        Genera la ruta remota para un gráfico local.
        Sanitiza el nombre del archivo para compatibilidad con Supabase Storage.
        
        Args:
            local_path: Ruta local del archivo
            user_id: UUID del usuario
        
        Returns:
            Ruta remota en el bucket (solo {user_id}/filename_sanitizado.ext)
        
        Examples:
            >>> from pathlib import Path
            >>> SupabaseConfig.remote_chart_path_for(Path("charts/assets/^SPX_chart.html"), "user-123")
            "user-123/_CARET_SPX_chart.html"
        """
        # Extraer solo el nombre del archivo
        filename = local_path.name
        
        # Sanitizar el nombre del archivo para Supabase Storage
        sanitized_filename = cls.sanitize_filename_for_storage(filename)

        return cls.build_chart_path(sanitized_filename, user_id)


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


def get_logger(name: str) -> logging.Logger:
    """
    Crea y configura un logger.
    
    Args:
        name: Nombre del logger (usualmente __name__)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Solo configurar si no tiene handlers (evitar duplicados)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    return logger

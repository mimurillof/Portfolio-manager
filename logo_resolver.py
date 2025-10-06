"""Utilidades para resolver URLs de logos de compañías.

Prioriza los datos proporcionados por yfinance; cuando no están
presentes, deriva un logo consistente usando dominios conocidos o
metadatos como el sitio web oficial del activo. La implementación se
mantiene libre de efectos secundarios: no realiza solicitudes HTTP, solo
construye URLs que pueden ser consumidas por el frontend.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse

CLEARBIT_BASE_URL = "https://logo.clearbit.com/{domain}"

# Conjunto de símbolos que usamos habitualmente en los dashboards. Los
# dominios provienen de las fuentes oficiales de cada compañía.
SYMBOL_DOMAIN_OVERRIDES = {
    "AAPL": "apple.com",
    "TSLA": "tesla.com",
    "MSFT": "microsoft.com",
    "GOOG": "google.com",
    "GOOGL": "google.com",
    "AMZN": "amazon.com",
    "SPOT": "spotify.com",
    "DIS": "disney.com",
    "NVDA": "nvidia.com",
    "META": "meta.com",
    "JPM": "jpmorganchase.com",
    "NFLX": "netflix.com",
    "BRK.B": "berkshirehathaway.com",
    "BAC": "bankofamerica.com",
    "V": "visa.com",
    "MA": "mastercard.com",
    "KO": "coca-colacompany.com",
    "PEP": "pepsico.com",
    "XOM": "exxonmobil.com",
    "CVX": "chevron.com",
}


def _normalize_domain(raw_url: str) -> Optional[str]:
    """Extrae un dominio normalizado a partir de una URL genérica."""
    if not raw_url:
        return None

    raw_url = raw_url.strip()
    if not raw_url:
        return None

    parsed = urlparse(raw_url if raw_url.startswith(("http://", "https://")) else f"https://{raw_url}")
    hostname = parsed.hostname

    if not hostname:
        return None

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname.lower()


@lru_cache(maxsize=None)
def resolve_logo_url(symbol: str, website: Optional[str] = None) -> Optional[str]:
    """Devuelve una URL de logo para ``symbol``.

    Se evalúa en este orden:
    1. Dominio conocido en ``SYMBOL_DOMAIN_OVERRIDES``.
    2. Dominio derivado del parámetro ``website``.

    Args:
        symbol: ticker bursátil (insensible a mayúsculas/minúsculas).
        website: URL del sitio oficial proveniente de yfinance (opcional).

    Returns:
        URL del logo lista para consumir o ``None`` si no se pudo
        determinar una fuente confiable.
    """
    if not symbol:
        return None

    normalized_symbol = symbol.strip().upper()
    if not normalized_symbol:
        return None

    domain = SYMBOL_DOMAIN_OVERRIDES.get(normalized_symbol)

    if not domain:
        domain = _normalize_domain(website or "")

    if not domain:
        return None

    return CLEARBIT_BASE_URL.format(domain=domain)


__all__ = ["resolve_logo_url", "SYMBOL_DOMAIN_OVERRIDES"]

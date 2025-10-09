"""
Módulo para obtener datos de mercado usando yfinance.

Extiende la obtención de datos con scraping ligero hacia Yahoo Finance para
listas de ganadores, perdedores y acciones más activas.
"""
from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import yfinance as yf

from logo_resolver import resolve_logo_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Clase para obtener datos de mercado usando yfinance"""

    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self._weekly_cache: Dict[str, List[float]] = {}
        self._market_movers_cache: Dict[str, pd.DataFrame] = {}
        self._market_movers_cache_time: Optional[datetime] = None
    
    def get_stock_data(
        self, 
        symbol: str, 
        period: str = "6mo", 
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos de una acción
        
        Args:
            symbol: Símbolo del ticker (ej: AAPL)
            period: Periodo de tiempo (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Intervalo (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame con los datos históricos
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No se encontraron datos para {symbol}")
                return None
            
            return df
        
        except Exception as e:
            logger.error(f"Error obteniendo datos para {symbol}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Obtiene el precio actual de una acción
        
        Args:
            symbol: Símbolo del ticker
        
        Returns:
            Precio actual o None
        """
        cache_key = f"stock_info:{symbol.upper()}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            price = cached.get("current_price") if isinstance(cached, dict) else None
            if price is not None:
                return price

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            
            # Intentar obtener el precio actual de diferentes campos
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if price is None:
                # Fallback: obtener el último precio del histórico
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
            
            price_value = float(price) if price else None
            if cache_key in self.cache and isinstance(self.cache[cache_key], dict):
                self.cache[cache_key]["current_price"] = price_value
            return price_value
        
        except Exception as e:
            logger.error(f"Error obteniendo precio actual para {symbol}: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Obtiene información detallada de una acción usando yfinance."""
        cache_key = f"stock_info_{symbol}"
        
        # Verificar caché
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if isinstance(cached, dict) and cached.get("symbol") == symbol:
                return cached

        try:
            ticker = yf.Ticker(symbol)

            # yfinance expone un diccionario ligero en ``info``; si no incluye el logo
            # intentamos enriquecerlo con ``get_info`` que devuelve metadatos adicionales.
            info: Dict[str, Any] = {}
            try:
                info = ticker.info or {}
            except Exception as info_error:
                logger.debug("No se pudo obtener info rápida para %s: %s", symbol, info_error)

            if not info.get("logo_url") and not info.get("logoUrl"):
                try:
                    detailed_info = ticker.get_info()
                    if isinstance(detailed_info, dict):
                        # Conservamos los datos existentes priorizando los valores nuevos.
                        info = {**info, **detailed_info}
                except Exception as detailed_error:
                    logger.debug("No se pudo obtener info detallada para %s: %s", symbol, detailed_error)

            logo_url = info.get("logo_url") or info.get("logoUrl")

            if not logo_url:
                website_url = (
                    info.get("website")
                    or info.get("websiteUrl")
                    or info.get("website_url")
                )
                fallback_logo = resolve_logo_url(symbol, website_url)
                if fallback_logo:
                    logo_url = fallback_logo

            # Obtener datos históricos para calcular cambio porcentual
            hist = ticker.history(period="5d")
            current_price = self.get_current_price(symbol)

            if current_price and len(hist) >= 2:
                previous_close = hist['Close'].iloc[-2]
                change_percent = ((current_price - previous_close) / previous_close) * 100
            else:
                change_percent = 0

            result = {
                "symbol": symbol,
                "name": info.get('longName') or info.get('shortName') or symbol,
                "current_price": current_price,
                "change_percent": change_percent,
                "market_cap": info.get('marketCap'),
                "volume": info.get('volume'),
                "logo_url": logo_url,
                "exchange": info.get('exchange'),
                "currency": info.get('currency', 'USD'),
            }

            self.cache[cache_key] = result
            return result

        except Exception as e:
            logger.error(f"Error obteniendo información para {symbol}: {e}")
            fallback = {
                "symbol": symbol,
                "name": symbol,
                "current_price": None,
                "change_percent": 0,
                "market_cap": None,
                "volume": None,
                "logo_url": None,
                "exchange": None,
                "currency": "USD",
            }
            self.cache[cache_key] = fallback
            return fallback
    
    def get_multiple_stocks_info(self, symbols: List[str]) -> List[Dict]:
        """
        Obtiene información de múltiples acciones
        
        Args:
            symbols: Lista de símbolos
        
        Returns:
            Lista de diccionarios con información de cada ticker
        """
        results = []
        for symbol in symbols:
            info = self.get_stock_info(symbol)
            results.append(info)
        
        return results
    
    def get_historical_data_range(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos en un rango de fechas
        
        Args:
            symbol: Símbolo del ticker
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            DataFrame con los datos históricos
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                logger.warning(f"No se encontraron datos para {symbol} en el rango especificado")
                return None
            
            return df
        
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos para {symbol}: {e}")
            return None
    
    def get_intraday_data(self, symbol: str, period: str = "1d", interval: str = "5m") -> Optional[pd.DataFrame]:
        """
        Obtiene datos intradiarios
        
        Args:
            symbol: Símbolo del ticker
            period: Periodo (1d, 5d, 1mo)
            interval: Intervalo (1m, 2m, 5m, 15m, 30m, 60m, 90m)
        
        Returns:
            DataFrame con datos intradiarios
        """
        return self.get_stock_data(symbol, period=period, interval=interval)
    
    def get_weekly_performance(self, symbol: str) -> Optional[List[float]]:
        """
        Obtiene el rendimiento de los últimos 7 días
        
        Args:
            symbol: Símbolo del ticker
        
        Returns:
            Lista de precios de cierre de los últimos 7 días
        """
        cache_key = f"weekly:{symbol.upper()}"
        if cache_key in self._weekly_cache:
            return self._weekly_cache[cache_key]

        try:
            df = self.get_stock_data(symbol, period="1mo", interval="1d")
            
            if df is None or df.empty:
                return None
            
            # Obtener los últimos 7 días
            last_7_days = df['Close'].tail(7).tolist()
            self._weekly_cache[cache_key] = last_7_days
            return last_7_days
        
        except Exception as e:
            logger.error(f"Error obteniendo rendimiento semanal para {symbol}: {e}")
            return None

    # ------------------------------------------------------------------
    # Market movers (scraping Yahoo Finance)
    # ------------------------------------------------------------------

    _MARKET_MOVER_URLS = {
        "gainers": "https://finance.yahoo.com/gainers",
        "losers": "https://finance.yahoo.com/losers",
        "active": "https://finance.yahoo.com/most-active",
        "viewed": "https://finance.yahoo.com/trending-tickers",
    }

    _MARKET_MOVER_COLUMNS = {
        "Symbol": "symbol",
        "Name": "name",
        "Price (Intraday)": "price",
        "Change": "change",
        "% Change": "percent_change",
        "Volume": "volume",
        "Avg Vol (3 month)": "avg_volume",
        "Avg Vol (3 months)": "avg_volume",
        "Market Cap": "market_cap",
    }

    _REQUEST_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def _should_use_cached_market_movers(self) -> bool:
        """Cache de 15 minutos para market movers"""
        if not self._market_movers_cache_time:
            return False
        elapsed = datetime.utcnow() - self._market_movers_cache_time
        return elapsed < timedelta(minutes=15)

    def _fetch_market_movers_from_web(self, mover_type: str) -> Optional[pd.DataFrame]:
        url = self._MARKET_MOVER_URLS.get(mover_type)
        if not url:
            logger.error("Tipo de market mover inválido: %s", mover_type)
            return None

        try:
            response = requests.get(url, headers=self._REQUEST_HEADERS, timeout=20)
            response.raise_for_status()
            
            # Usar StringIO para evitar el FutureWarning de pandas
            from io import StringIO
            tables = pd.read_html(StringIO(response.text))
            
            if not tables:
                logger.warning("No se encontraron tablas para %s", mover_type)
                return None
            table = tables[0]
            return table
        except requests.RequestException as exc:
            logger.error("Error HTTP al obtener market movers (%s): %s", mover_type, exc)
        except ValueError:
            logger.warning("No se pudieron parsear tablas HTML para %s", mover_type)
        except Exception:
            logger.exception("Error inesperado al obtener market movers (%s)", mover_type)
        return None

    @staticmethod
    def _normalize_percent(value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
            if match:
                try:
                    return float(match.group())
                except ValueError:
                    return None
        return None

    @staticmethod
    def _normalize_number(value: Any) -> Optional[float]:
        if value in (None, "--"):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace(",", "")
            multipliers = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
            suffix = cleaned[-1]
            if suffix in multipliers:
                try:
                    number = float(cleaned[:-1])
                    return number * multipliers[suffix]
                except ValueError:
                    return None
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def get_market_movers(self, mover_type: str) -> Optional[pd.DataFrame]:
        """Obtiene y cachea tablas de Yahoo Finance para market movers."""

        if self._should_use_cached_market_movers() and mover_type in self._market_movers_cache:
            logger.info(f"Usando caché para {mover_type}")
            return self._market_movers_cache[mover_type]

        # Delay para evitar rate limiting
        time.sleep(0.5)
        
        table = self._fetch_market_movers_from_web(mover_type)
        if table is None:
            return None

        normalized_columns = {
            column: self._MARKET_MOVER_COLUMNS.get(column, column)
            for column in table.columns
        }
        table = table.rename(columns=normalized_columns)

        if "symbol" not in table.columns:
            logger.warning("Tabla de %s no contiene columna 'symbol'", mover_type)
            return None

        # Normalizar columnas numéricas si existen
        if "percent_change" in table.columns:
            table["percent_change"] = table["percent_change"].apply(self._normalize_percent)
        if "change" in table.columns:
            table["change"] = table["change"].apply(self._normalize_number)
        if "price" in table.columns:
            table["price"] = table["price"].apply(self._normalize_number)
        if "volume" in table.columns:
            table["volume"] = table["volume"].apply(self._normalize_number)
        if "avg_volume" in table.columns:
            table["avg_volume"] = table["avg_volume"].apply(self._normalize_number)
        if "market_cap" in table.columns:
            table["market_cap"] = table["market_cap"].apply(self._normalize_number)

        self._market_movers_cache[mover_type] = table
        self._market_movers_cache_time = datetime.utcnow()
        return table

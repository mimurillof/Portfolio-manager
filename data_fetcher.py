"""
Módulo para obtener datos de mercado usando yfinance
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import logging

from logo_resolver import resolve_logo_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Clase para obtener datos de mercado usando yfinance"""
    
    def __init__(self):
        self.cache = {}
    
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
            
            return float(price) if price else None
        
        except Exception as e:
            logger.error(f"Error obteniendo precio actual para {symbol}: {e}")
            return None
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Obtiene información detallada de una acción usando yfinance."""

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

            return {
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

        except Exception as e:
            logger.error(f"Error obteniendo información para {symbol}: {e}")
            return {
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
        try:
            df = self.get_stock_data(symbol, period="1mo", interval="1d")
            
            if df is None or df.empty:
                return None
            
            # Obtener los últimos 7 días
            last_7_days = df['Close'].tail(7).tolist()
            
            return last_7_days
        
        except Exception as e:
            logger.error(f"Error obteniendo rendimiento semanal para {symbol}: {e}")
            return None

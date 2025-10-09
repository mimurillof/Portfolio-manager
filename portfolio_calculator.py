"""
Módulo para realizar cálculos del portafolio
"""
import pandas as pd
import numpy as np
import time
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from data_fetcher import DataFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioCalculator:
    """Clase para realizar cálculos del portafolio"""
    
    def __init__(self, data_fetcher: DataFetcher):
        self.data_fetcher = data_fetcher
    
    def calculate_portfolio_value(self, assets: List[Dict]) -> Dict:
        """
        Calcula el valor total del portafolio y métricas
        
        Args:
            assets: Lista de activos con formato {"symbol": str, "units": int}
        
        Returns:
            Diccionario con métricas del portafolio
        """
        total_value = 0
        total_change = 0
        total_change_absolute = 0
        assets_data = []
        
        for asset in assets:
            symbol = asset["symbol"]
            units = asset["units"]
            
            info = self.data_fetcher.get_stock_info(symbol)
            
            if info["current_price"] is None:
                logger.warning(f"No se pudo obtener precio para {symbol}")
                continue
            
            position_value = info["current_price"] * units
            position_change = position_value * (info["change_percent"] / 100)
            
            total_value += position_value
            total_change_absolute += position_change
            
            # Obtener datos de rendimiento semanal para sparklines
            weekly_perf = self.data_fetcher.get_weekly_performance(symbol)
            
            assets_data.append({
                "symbol": symbol,
                "name": info["name"],
                "units": units,
                "current_price": info["current_price"],
                "position_value": position_value,
                "change_percent": info["change_percent"],
                "change_absolute": position_change,
                "logo_url": info.get("logo_url"),
                "market_cap": info["market_cap"],
                "volume": info["volume"],
                "weekly_performance": weekly_perf,
            })
        
        if total_value > 0:
            total_change = (total_change_absolute / (total_value - total_change_absolute)) * 100
        
        return {
            "total_value": total_value,
            "total_change_percent": total_change,
            "total_change_absolute": total_change_absolute,
            "assets": assets_data,
            "timestamp": datetime.now().isoformat(),
        }
    
    def calculate_portfolio_performance(
        self, 
        assets: List[Dict], 
        period: str = "6mo"
    ) -> pd.DataFrame:
        """
        Calcula el rendimiento histórico del portafolio
        
        Args:
            assets: Lista de activos con formato {"symbol": str, "units": int}
            period: Periodo de tiempo
        
        Returns:
            DataFrame con el rendimiento del portafolio
        """
        portfolio_values = None
        
        for asset in assets:
            symbol = asset["symbol"]
            units = asset["units"]
            
            hist_data = self.data_fetcher.get_stock_data(symbol, period=period)
            
            if hist_data is None or hist_data.empty:
                logger.warning(f"No se encontraron datos históricos para {symbol}")
                continue
            
            # Calcular valor de la posición
            position_values = hist_data['Close'] * units
            
            if portfolio_values is None:
                portfolio_values = position_values
            else:
                # Alinear índices y sumar
                portfolio_values = portfolio_values.add(position_values, fill_value=0)
        
        if portfolio_values is None:
            return pd.DataFrame()
        
        # Convertir a DataFrame
        df = pd.DataFrame({
            'portfolio_value': portfolio_values,
            'date': portfolio_values.index
        })
        
        df = df.reset_index(drop=True)
        
        return df
    
    def get_top_gainers_losers(self, assets_data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Identifica los mayores ganadores y perdedores
        
        Args:
            assets_data: Lista de datos de activos
        
        Returns:
            Tupla con (ganadores, perdedores)
        """
        sorted_by_change = sorted(assets_data, key=lambda x: x["change_percent"], reverse=True)
        
        gainers = [asset for asset in sorted_by_change if asset["change_percent"] > 0]
        losers = [asset for asset in sorted_by_change if asset["change_percent"] < 0]
        
        return gainers, losers
    
    def calculate_asset_allocation(self, assets_data: List[Dict]) -> List[Dict]:
        """
        Calcula la distribución de activos en el portafolio
        
        Args:
            assets_data: Lista de datos de activos
        
        Returns:
            Lista de activos con porcentaje de participación
        """
        total_value = sum(asset["position_value"] for asset in assets_data)
        
        allocation = []
        for asset in assets_data:
            percentage = (asset["position_value"] / total_value * 100) if total_value > 0 else 0
            allocation.append({
                **asset,
                "allocation_percent": percentage
            })
        
        return allocation
    
    def calculate_portfolio_metrics(self, performance_df: pd.DataFrame) -> Dict:
        """
        Calcula métricas adicionales del portafolio
        
        Args:
            performance_df: DataFrame con el rendimiento del portafolio
        
        Returns:
            Diccionario con métricas
        """
        if performance_df.empty:
            return {}

        values = performance_df['portfolio_value'].to_numpy(dtype=float)
        
        # Calcular retornos
        returns = np.diff(values) / values[:-1]
        
        # Métricas
        total_return = (values[-1] - values[0]) / values[0] * 100 if values[0] > 0 else 0
        volatility = np.std(returns) * np.sqrt(252) * 100  # Anualizada
        sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
        
        # Máximo drawdown
        cumulative = (1 + returns).cumprod()
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown) * 100
        
        return {
            "total_return_percent": total_return,
            "volatility_percent": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown_percent": max_drawdown,
        }
    
    def get_market_overview(
        self,
        watchlist: List[Dict],
        *,
        source_data: Optional[Dict] = None,
        top_n: int = 10,
        use_persisted: bool = True,
    ) -> Dict[str, List[Dict]]:
        """Obtiene listas de movimiento del mercado combinando watchlist y scraping."""

        persisted = None
        if use_persisted and source_data and isinstance(source_data, dict):
            persisted = source_data.get("market_overview")
            if isinstance(persisted, dict):
                normalized = {
                    key: [dict(item) for item in value if isinstance(item, dict)]
                    for key, value in persisted.items()
                    if isinstance(value, list)
                }

                # Solo reutilizar datos persistidos si contienen todas las listas necesarias
                if (
                    normalized.get("all")
                    and normalized.get("gainers")
                    and normalized.get("losers")
                    and normalized.get("most_active")
                ):
                    return normalized

        market_data_map: Dict[str, Dict[str, Dict[str, Any]]] = {
            "watchlist": {},
            "viewed": {},
            "gainers": {},
            "losers": {},
            "active": {},
        }

        def upsert(target: str, symbol: str, payload: Dict[str, Any]) -> None:
            existing = market_data_map[target].get(symbol, {})
            merged = {**existing, **{k: v for k, v in payload.items() if v is not None}}
            market_data_map[target][symbol] = merged

        # Procesar watchlist con delay para evitar rate limiting
        for idx, item in enumerate(watchlist):
            symbol = item.get("symbol")
            if not symbol:
                continue

            # Delay progresivo para evitar rate limiting
            if idx > 0:
                time.sleep(0.3)

            info = self.data_fetcher.get_stock_info(symbol)
            weekly_perf = self.data_fetcher.get_weekly_performance(symbol)
            
            payload = {
                "symbol": symbol,
                "name": item.get("name", info.get("name", symbol)),
                "exchange": item.get("exchange", info.get("exchange")),
                "current_price": info.get("current_price"),
                "change_percent": info.get("change_percent"),
                "market_cap": info.get("market_cap"),
                "volume": info.get("volume"),
                "logo_url": info.get("logo_url"),
                "weekly_performance": weekly_perf,
            }
            upsert("watchlist", symbol, payload)
            if payload["change_percent"] is not None:
                if payload["change_percent"] > 0:
                    upsert("gainers", symbol, payload)
                elif payload["change_percent"] < 0:
                    upsert("losers", symbol, payload)

        movers_map = {
            "gainers": "gainers",
            "losers": "losers",
            "active": "active",
            "viewed": "viewed",
        }

        # Procesar market movers con límite y delay
        for mover_type, bucket in movers_map.items():
            table = self.data_fetcher.get_market_movers(mover_type)
            if table is None:
                continue
            
            # Limitar a top_n elementos para reducir llamadas
            for idx, (_, row) in enumerate(table.head(top_n).iterrows()):
                symbol = str(row.get("symbol", "")).upper()
                if not symbol:
                    continue
                
                # Delay para evitar rate limiting en yfinance
                if idx > 0:
                    time.sleep(0.2)
                
                # Solo obtener info si no está ya cacheada
                info = self.data_fetcher.get_stock_info(symbol)
                weekly_perf = self.data_fetcher.get_weekly_performance(symbol)

                payload = {
                    "symbol": symbol,
                    "name": row.get("name") or info.get("name", symbol),
                    "exchange": info.get("exchange"),
                    "current_price": row.get("price") or info.get("current_price"),
                    "change_percent": row.get("percent_change") or info.get("change_percent"),
                    "market_cap": row.get("market_cap") or info.get("market_cap"),
                    "volume": row.get("volume") or info.get("volume"),
                    "logo_url": info.get("logo_url"),
                    "weekly_performance": weekly_perf,
                    "source": mover_type,
                }

                if bucket == "active":
                    upsert("active", symbol, payload)
                else:
                    upsert(bucket, symbol, payload)
                upsert("viewed", symbol, payload)

        def sort_bucket(bucket: Dict[str, Dict[str, Any]], *, key: str, reverse: bool = True) -> List[Dict]:
            items = list(bucket.values())
            return sorted(
                items,
                key=lambda entry: (entry.get(key) or 0),
                reverse=reverse,
            )

        viewed_list = sort_bucket(market_data_map["viewed"], key="volume", reverse=True)
        watchlist_list = sort_bucket(market_data_map["watchlist"], key="change_percent", reverse=True)
        gainers_list = sort_bucket(market_data_map["gainers"], key="change_percent", reverse=True)
        losers_list = sort_bucket(market_data_map["losers"], key="change_percent", reverse=False)
        active_list = sort_bucket(market_data_map["active"], key="volume", reverse=True)

        def merge_unique(buckets: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
            merged: List[Dict[str, Any]] = []
            seen: set[str] = set()

            for bucket in buckets:
                for entry in bucket:
                    symbol = entry.get("symbol")
                    if not symbol or symbol in seen:
                        continue
                    merged.append(entry)
                    seen.add(symbol)
            return merged

        priority_buckets = [
            gainers_list,
            losers_list,
            active_list,
            viewed_list,
        ]

        all_list = merge_unique(priority_buckets)

        if not all_list:
            all_list = merge_unique([watchlist_list])

        # Añadir elementos de la watchlist sólo como relleno si aún faltan entradas.
        if len(all_list) < top_n * 2:
            watch_symbols = {entry.get("symbol") for entry in all_list}
            for item in watchlist_list:
                symbol = item.get("symbol")
                if not symbol or symbol in watch_symbols:
                    continue
                all_list.append(item)
                watch_symbols.add(symbol)
                if len(all_list) >= top_n * 2:
                    break

        response = {
            "all": all_list[: top_n * 2],
            "gainers": gainers_list[:top_n],
            "losers": losers_list[:top_n],
            "most_viewed": (viewed_list[:top_n] if viewed_list else watchlist_list[:top_n]),
            "most_active": active_list[:top_n],
        }

        return response

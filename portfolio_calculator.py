"""
Módulo para realizar cálculos del portafolio
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
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
    
    def get_market_overview(self, watchlist: List[Dict]) -> List[Dict]:
        """
        Obtiene un resumen del mercado basado en la watchlist
        
        Args:
            watchlist: Lista de símbolos para seguir
        
        Returns:
            Lista con información de mercado
        """
        market_data = []
        
        for item in watchlist:
            symbol = item["symbol"]
            info = self.data_fetcher.get_stock_info(symbol)
            weekly_perf = self.data_fetcher.get_weekly_performance(symbol)
            
            market_data.append({
                "symbol": symbol,
                "name": item.get("name", info["name"]),
                "exchange": item.get("exchange", info["exchange"]),
                "current_price": info["current_price"],
                "change_percent": info["change_percent"],
                "market_cap": info["market_cap"],
                "volume": info["volume"],
                "weekly_performance": weekly_perf,
            })
        
        return market_data

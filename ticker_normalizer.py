"""
Normalizador de símbolos de tickers para Yahoo Finance.
Convierte símbolos de la base de datos a formato compatible con yfinance.
"""
from typing import Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class TickerNormalizer:
    """Normaliza símbolos de tickers para compatibilidad con yfinance."""
    
    # Mapeo de símbolos comunes mal formateados
    KNOWN_CORRECTIONS = {
        # Criptomonedas
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
        "USDTUSD": "USDT-USD",
        "BNBUSD": "BNB-USD",
        "XRPUSD": "XRP-USD",
        "ADAUSD": "ADA-USD",
        "SOLUSD": "SOL-USD",
        "DOGEUSD": "DOGE-USD",
        
        # Variantes europeas/internacionales comunes
        "NVD.F": "NVDA",      # NVIDIA en Frankfurt → NASDAQ
        "AAPL.F": "AAPL",     # Apple en Frankfurt → NASDAQ
        "MSFT.F": "MSFT",     # Microsoft en Frankfurt → NASDAQ
        "AMZN.F": "AMZN",     # Amazon en Frankfurt → NASDAQ
        "TSLA.F": "TSLA",     # Tesla en Frankfurt → NASDAQ
        "GOOGL.F": "GOOGL",   # Alphabet en Frankfurt → NASDAQ
        "META.F": "META",     # Meta en Frankfurt → NASDAQ
        
        # Otros errores comunes
        "BRK.B": "BRK-B",     # Berkshire Hathaway Class B
        "BRK.A": "BRK-A",     # Berkshire Hathaway Class A
    }
    
    # Sufijos válidos de exchanges
    VALID_SUFFIXES = {
        # USA
        "",           # NASDAQ/NYSE por defecto
        # Europa
        ".L",         # London Stock Exchange
        ".F",         # Frankfurt
        ".PA",        # Paris
        ".MI",        # Milan
        ".AS",        # Amsterdam
        ".SW",        # Switzerland
        # Asia
        ".T",         # Tokyo
        ".HK",        # Hong Kong
        ".SS",        # Shanghai
        ".SZ",        # Shenzhen
        # América Latina
        ".SA",        # São Paulo
        ".MX",        # Mexico
        # Otros
        ".TO",        # Toronto
        ".AX",        # Australia
    }
    
    @classmethod
    def normalize(cls, symbol: str) -> str:
        """
        Normaliza un símbolo de ticker para ser compatible con yfinance.
        
        Args:
            symbol: Símbolo original de la base de datos
        
        Returns:
            Símbolo normalizado compatible con yfinance
        
        Examples:
            >>> TickerNormalizer.normalize("BTCUSD")
            "BTC-USD"
            >>> TickerNormalizer.normalize("NVD.F")
            "NVDA"
            >>> TickerNormalizer.normalize("AAPL")
            "AAPL"
        """
        if not symbol:
            logger.warning("Símbolo vacío recibido para normalización")
            return symbol
        
        original_symbol = symbol
        symbol = symbol.strip().upper()
        
        # 1. Verificar si está en el mapeo conocido
        if symbol in cls.KNOWN_CORRECTIONS:
            normalized = cls.KNOWN_CORRECTIONS[symbol]
            logger.debug(f"Ticker corregido: {original_symbol} → {normalized}")
            return normalized
        
        # 2. Detectar y corregir criptomonedas sin guion
        # Patrón: 3-5 letras seguidas de USD/USDT sin guion
        crypto_pattern = r'^([A-Z]{3,5})(USD[T]?)$'
        crypto_match = re.match(crypto_pattern, symbol)
        if crypto_match:
            base = crypto_match.group(1)
            quote = crypto_match.group(2)
            normalized = f"{base}-{quote}"
            logger.debug(f"Cripto corregida: {original_symbol} → {normalized}")
            return normalized
        
        # 3. Detectar símbolos con sufijos inválidos (.F, .DE, etc.) 
        # que deberían ser símbolos USA estándar
        if '.' in symbol:
            base, suffix = symbol.rsplit('.', 1)
            suffix_with_dot = f".{suffix}"
            
            # Si el sufijo no es válido, quitar el sufijo
            if suffix_with_dot not in cls.VALID_SUFFIXES:
                # Verificar si es una variante conocida
                potential_us_symbol = base
                if potential_us_symbol in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", 
                                           "META", "NVDA", "AMD", "NFLX", "DIS"]:
                    logger.debug(f"Sufijo inválido removido: {original_symbol} → {potential_us_symbol}")
                    return potential_us_symbol
        
        # 4. Corregir símbolos con puntos que deberían tener guiones
        # Ejemplo: BRK.B → BRK-B
        if '.' in symbol and not any(symbol.endswith(suf) for suf in cls.VALID_SUFFIXES):
            normalized = symbol.replace('.', '-')
            logger.debug(f"Punto reemplazado por guion: {original_symbol} → {normalized}")
            return normalized
        
        # 5. Si no hay correcciones necesarias, retornar como está
        if original_symbol != symbol:
            logger.debug(f"Ticker normalizado (solo uppercase): {original_symbol} → {symbol}")
        
        return symbol
    
    @classmethod
    def normalize_batch(cls, symbols: list) -> Dict[str, str]:
        """
        Normaliza un batch de símbolos.
        
        Args:
            symbols: Lista de símbolos originales
        
        Returns:
            Diccionario {símbolo_original: símbolo_normalizado}
        """
        result = {}
        for symbol in symbols:
            result[symbol] = cls.normalize(symbol)
        return result
    
    @classmethod
    def add_custom_mapping(cls, original: str, corrected: str):
        """
        Agrega un mapeo personalizado en runtime.
        
        Args:
            original: Símbolo original
            corrected: Símbolo corregido
        """
        cls.KNOWN_CORRECTIONS[original.upper()] = corrected.upper()
        logger.info(f"Mapeo personalizado agregado: {original} → {corrected}")
    
    @classmethod
    def is_ticker_valid_in_yfinance(cls, symbol: str) -> bool:
        """
        Verifica si un ticker es válido consultando directamente yfinance.
        
        Args:
            symbol: Símbolo a verificar
        
        Returns:
            True si el ticker existe en yfinance, False en caso contrario
        """
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            
            # Intentar obtener información básica
            info = ticker.info
            
            # Si info está vacío o solo tiene 'trailingPegRatio', el ticker no existe
            if not info or (len(info) == 1 and 'trailingPegRatio' in info):
                return False
            
            # Verificar que tenga datos mínimos (símbolo, currency, etc.)
            if 'symbol' in info or 'currency' in info or 'regularMarketPrice' in info:
                return True
            
            # Fallback: intentar obtener historial reciente
            hist = ticker.history(period="5d")
            return not hist.empty
            
        except Exception as e:
            logger.debug(f"Error verificando ticker {symbol} en yfinance: {e}")
            return False
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> bool:
        """
        Valida si un símbolo tiene un formato razonable.
        
        Args:
            symbol: Símbolo a validar
        
        Returns:
            True si el símbolo parece válido
        """
        if not symbol:
            return False
        
        symbol = symbol.strip().upper()
        
        # Debe tener al menos 1 carácter
        if len(symbol) < 1:
            return False
        
        # Puede contener letras, números, guiones, puntos y ^ (para índices)
        # Índices como ^SPX, ^GSPC, ^DJI, ^IXIC son válidos en Yahoo Finance
        if not re.match(r'^[\^A-Z0-9.\-]+$', symbol):
            return False
        
        # No puede empezar o terminar con guion o punto (pero sí con ^)
        if symbol.startswith(('-', '.')) or symbol.endswith(('-', '.')):
            return False
        
        return True


# Función de conveniencia para usar directamente
def normalize_ticker(symbol: str) -> str:
    """
    Función de conveniencia para normalizar un ticker.
    
    Args:
        symbol: Símbolo original
    
    Returns:
        Símbolo normalizado
    """
    return TickerNormalizer.normalize(symbol)


# Para testing
if __name__ == "__main__":
    # Ejemplos de uso
    test_cases = [
        "BTCUSD",
        "NVD.F",
        "AAPL",
        "BRK.B",
        "ETHUSD",
        "MSFT.F",
        "GOOGL",
        "   tsla  ",
        "BTC-USD",  # Ya correcto
    ]
    
    print("=" * 60)
    print("TEST DE NORMALIZACIÓN DE TICKERS")
    print("=" * 60)
    
    for symbol in test_cases:
        normalized = normalize_ticker(symbol)
        status = "✓" if normalized != symbol.strip().upper() else "→"
        print(f"{status} {symbol:15s} → {normalized}")
    
    print("\nValidación de símbolos:")
    valid_test = ["AAPL", "BTC-USD", ".INVALID", "VAL1D", ""]
    for symbol in valid_test:
        is_valid = TickerNormalizer.validate_symbol(symbol)
        status = "✓" if is_valid else "✗"
        print(f"{status} '{symbol}' → {'Válido' if is_valid else 'Inválido'}")

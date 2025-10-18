# Normalización de Tickers - Guía Técnica

## 🎯 Problema

Los símbolos de activos (tickers) almacenados en la base de datos pueden estar en formatos incompatibles con la API de Yahoo Finance (yfinance), causando errores al obtener datos de mercado.

### Ejemplos de Problemas Comunes

| ❌ En Base de Datos | ✅ Formato yfinance | Tipo de Error |
|---------------------|---------------------|---------------|
| `BTCUSD`            | `BTC-USD`           | Cripto sin guion |
| `NVD.F`             | `NVDA`              | Sufijo europeo incorrecto |
| `AAPL.F`            | `AAPL`              | Exchange innecesario |
| `BRK.B`             | `BRK-B`             | Punto en lugar de guion |
| `ETHUSD`            | `ETH-USD`           | Cripto sin guion |

---

## 🔧 Solución: TickerNormalizer

El módulo `ticker_normalizer.py` implementa un sistema de normalización automática con las siguientes estrategias:

### 1. Mapeo de Correcciones Conocidas

Diccionario predefinido de correcciones comunes:

```python
KNOWN_CORRECTIONS = {
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
    "NVD.F": "NVDA",
    "BRK.B": "BRK-B",
    # ... más
}
```

### 2. Detección Inteligente de Criptomonedas

Patrón regex que detecta criptos sin guion:

```
Patrón: ^([A-Z]{3,5})(USD[T]?)$
Ejemplo: BTCUSD → BTC-USD
```

### 3. Limpieza de Sufijos Inválidos

Remueve sufijos de exchanges europeos cuando el símbolo base es USA:

```
NVD.F → NVDA (sufijo .F inválido para NVIDIA)
AAPL.F → AAPL (sufijo .F innecesario)
```

### 4. Conversión de Puntos a Guiones

Para clases de acciones:

```
BRK.B → BRK-B (Berkshire Hathaway Class B)
```

---

## 🚀 Uso

### En Portfolio Processor (Automático)

El procesador de portfolios usa automáticamente el normalizador:

```python
# En portfolio_processor.py
from ticker_normalizer import TickerNormalizer

# Se normaliza automáticamente en _transform_assets_format()
normalized_symbol = TickerNormalizer.normalize(db_symbol)
```

### Uso Directo

```python
from ticker_normalizer import normalize_ticker

# Normalizar un símbolo
symbol = normalize_ticker("BTCUSD")
print(symbol)  # Output: BTC-USD

# Normalizar múltiples
from ticker_normalizer import TickerNormalizer

symbols = ["BTCUSD", "NVD.F", "AAPL"]
mapping = TickerNormalizer.normalize_batch(symbols)
# {"BTCUSD": "BTC-USD", "NVD.F": "NVDA", "AAPL": "AAPL"}
```

### Agregar Mapeos Personalizados

```python
from ticker_normalizer import TickerNormalizer

# Agregar corrección específica en runtime
TickerNormalizer.add_custom_mapping("CUSTOM", "CUSTOM-USD")

# Ahora "CUSTOM" se normalizará a "CUSTOM-USD"
normalized = TickerNormalizer.normalize("CUSTOM")
```

---

## 🧪 Testing

Ejecutar el módulo directamente para ver ejemplos:

```bash
python ticker_normalizer.py
```

**Output esperado:**

```
============================================================
TEST DE NORMALIZACIÓN DE TICKERS
============================================================
✓ BTCUSD          → BTC-USD
✓ NVD.F           → NVDA
→ AAPL            → AAPL
✓ BRK.B           → BRK-B
✓ ETHUSD          → ETH-USD
✓ MSFT.F          → MSFT
→ GOOGL           → GOOGL
✓    tsla         → TSLA
→ BTC-USD         → BTC-USD

Validación de símbolos:
✓ 'AAPL' → Válido
✓ 'BTC-USD' → Válido
✗ '.INVALID' → Inválido
✓ 'VAL1D' → Válido
✗ '' → Inválido
```

---

## 📋 Reglas de Normalización

### 1. Uppercase y Trim

**Siempre** se convierte a mayúsculas y se eliminan espacios:

```python
"  aapl  " → "AAPL"
"tsla" → "TSLA"
```

### 2. Validación de Formato

Símbolos deben cumplir:
- Al menos 1 carácter
- Solo letras, números, guiones y puntos
- No empezar/terminar con guion o punto

```python
TickerNormalizer.validate_symbol("AAPL")     # True
TickerNormalizer.validate_symbol(".INVALID") # False
TickerNormalizer.validate_symbol("-INVALID") # False
```

### 3. Prioridad de Correcciones

1. **Mapeo conocido** (KNOWN_CORRECTIONS)
2. **Patrón de criptomonedas** (regex)
3. **Sufijos inválidos** (exchanges)
4. **Puntos → Guiones** (clases de acciones)
5. **Sin cambios** (ya está correcto)

---

## 🔍 Logging

El normalizador genera logs detallados:

```
DEBUG - Ticker corregido: BTCUSD → BTC-USD
DEBUG - Cripto corregida: ETHUSD → ETH-USD
DEBUG - Sufijo inválido removido: NVD.F → NVDA
DEBUG - Punto reemplazado por guion: BRK.B → BRK-B
INFO - Ticker normalizado: btcusd → BTC-USD
```

---

## ⚠️ Casos Especiales

### Criptomonedas con USDT

```python
"BTCUSDT" → "BTC-USDT"  # Detectado automáticamente
```

### Exchanges Válidos

Los siguientes sufijos **NO** se remueven:

```
.L   (London)
.PA  (Paris)
.T   (Tokyo)
.HK  (Hong Kong)
.SA  (São Paulo)
... y más
```

### Símbolos con Números

```python
"BERKB" → "BERKB"  # No se altera
"BRK.B" → "BRK-B"  # Punto → Guion
```

---

## 🛠️ Extender el Normalizador

### Agregar Nuevas Correcciones

Editar `ticker_normalizer.py`:

```python
KNOWN_CORRECTIONS = {
    # ... existentes ...
    "NUEVO": "NUEVO-USD",
    "OTRO.X": "OTRO",
}
```

### Agregar Nuevos Patrones

Modificar el método `normalize()`:

```python
# Ejemplo: detectar símbolos con prefijo "X-"
if symbol.startswith("X-"):
    return symbol[2:]  # Remover prefijo
```

---

## 📊 Impacto en el Sistema

### Antes (Sin Normalización)

```
ERROR: No se encontraron datos para BTCUSD
ERROR: No se encontraron datos para NVD.F
WARNING: Símbolo inválido: BRK.B
```

### Después (Con Normalización)

```
INFO: Ticker normalizado: BTCUSD → BTC-USD
INFO: Ticker normalizado: NVD.F → NVDA
INFO: Ticker normalizado: BRK.B → BRK-B
INFO: Datos obtenidos exitosamente para BTC-USD
INFO: Datos obtenidos exitosamente para NVDA
INFO: Datos obtenidos exitosamente para BRK-B
```

---

## 🎯 Mejores Prácticas

1. **Siempre normalizar** antes de llamar a yfinance
2. **Guardar símbolo original** para trazabilidad
3. **Loggear normalizaciones** para auditoría
4. **Validar símbolos** después de normalizar
5. **Actualizar KNOWN_CORRECTIONS** periódicamente

---

## 📈 Estadísticas de Uso

En `portfolio_processor.py`, cada asset se normaliza:

```python
# Transformación con normalización
original_symbol = "BTCUSD"
normalized_symbol = TickerNormalizer.normalize(original_symbol)

asset = {
    "symbol": normalized_symbol,        # "BTC-USD"
    "original_symbol": original_symbol, # "BTCUSD"
    "units": 10.5,
    # ...
}
```

---

**Fecha:** 17 de octubre de 2025  
**Versión:** 1.0.0  
**Autor:** AIDA (AI Data Architect)

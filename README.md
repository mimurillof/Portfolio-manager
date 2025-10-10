# Portfolio Manager 📊

Sistema completo de gestión y análisis de portafolio de inversiones con integración a yfinance y generación de gráficos con Plotly.

## 🚀 Características

- **Obtención de datos en tiempo real** usando yfinance API
- **Cálculos completos del portafolio**: valor total, rendimiento, distribución
- **Gráficos interactivos** con Plotly (HTML + PNG)
- **Análisis de mercado** con watchlist personalizable
- **Identificación de ganadores y perdedores**
- **Métricas avanzadas**: Sharpe Ratio, volatilidad, máximo drawdown
- **Integración lista con FastAPI backend**

## 📁 Estructura del Proyecto

```
Portfolio manager/
├── config.py                 # Configuración general y constantes
├── data_fetcher.py          # Obtención de datos de yfinance
├── portfolio_calculator.py  # Cálculos y métricas del portafolio
├── chart_generator.py       # Generación de gráficos con Plotly
├── portfolio_manager.py     # Orquestador principal
├── api_integration.py       # Servicios para integración con FastAPI
├── requirements.txt         # Dependencias Python
├── README.md               # Esta documentación
│
├── data/                   # Fallback local de datos JSON (Supabase Storage es la fuente principal)
│   ├── portfolio_data.json
│   └── market_data.json
│
├── charts/                 # Gráficos generados
│   ├── portfolio_chart.html
│   ├── portfolio_chart.png
│   ├── allocation_chart.html
│   └── assets/            # Gráficos individuales por activo
│       ├── AAPL_chart.html
│       ├── TSLA_chart.html
│       └── ...
│
└── output/                # Otros archivos de salida
```

## 🔧 Instalación

1. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

2. **Configurar portafolio** (editar `config.py`):
```python
PORTFOLIO_CONFIG = {
    "assets": [
        {"symbol": "AAPL", "units": 10, "name": "Apple"},
        {"symbol": "TSLA", "units": 20, "name": "Tesla"},
        # ... más activos
    ]
}
```

## 💻 Uso

### Uso Standalone (Línea de comandos)

```bash
python portfolio_manager.py
```

Esto generará:
- Reporte completo sincronizado en Supabase Storage (con fallback local JSON)
- Gráficos HTML y PNG
- Resumen en consola

### Integración con FastAPI

```python
# En tu backend FastAPI
from Portfolio_manager.api_integration import (
    get_portfolio_data_for_api,
    get_portfolio_summary_for_api,
    get_market_data_for_api,
    get_chart_html_for_api
)

# Ejemplo de endpoints
@app.get("/api/portfolio")
async def get_portfolio(period: str = "6mo", refresh: bool = False):
    data = get_portfolio_data_for_api(period=period, refresh=refresh)
    return data

@app.get("/api/portfolio/summary")
async def get_summary():
    summary = get_portfolio_summary_for_api()
    return summary

@app.get("/api/market")
async def get_market():
    market_data = get_market_data_for_api()
    return market_data

@app.get("/api/chart/{chart_type}")
async def get_chart(chart_type: str):
    html = get_chart_html_for_api(chart_type)
    return HTMLResponse(content=html)
```

### Uso Programático

```python
from portfolio_manager import PortfolioManager

# Crear instancia
manager = PortfolioManager()

# Generar reporte completo
report = manager.generate_full_report(period="6mo")

# Obtener solo resumen rápido
summary = manager.get_portfolio_summary()

# Obtener datos de mercado
market = manager.get_market_data()

# Agregar un activo
manager.add_asset_to_portfolio("NVDA", 5)
```

## 📊 Datos Generados

### Portfolio Data JSON
```json
{
  "generated_at": "2025-10-05T...",
  "period": "6mo",
  "summary": {
    "total_value": 12304.11,
    "total_change_percent": 3.65,
    "total_change_absolute": 5.30
  },
  "metrics": {
    "total_return_percent": 15.5,
    "volatility_percent": 18.2,
    "sharpe_ratio": 0.85,
    "max_drawdown_percent": -8.5
  },
  "assets": [...],
  "allocation": [...],
  "gainers": [...],
  "losers": [...],
  "market_overview": {
    "all": [...],
    "gainers": [...],
    "losers": [...],
    "most_viewed": [...]
  }
}
```

## 🎨 Gráficos Generados

1. **Portfolio Performance Chart** (`portfolio_chart.html/png`)
   - Rendimiento histórico del portafolio completo
   - Área sombreada bajo la línea

2. **Allocation Pie Chart** (`allocation_chart.html/png`)
   - Distribución porcentual de activos
   - Gráfico de dona interactivo

3. **Individual Asset Charts** (`assets/SYMBOL_chart.html/png`)
   - Gráfico de velas (candlestick) por activo
   - Precios OHLC históricos

## 🔄 Flujo de Datos

```
1. yfinance API → data_fetcher.py
2. data_fetcher.py → portfolio_calculator.py
3. portfolio_calculator.py → portfolio_manager.py
4. portfolio_manager.py → chart_generator.py
5. chart_generator.py → HTML/PNG files
6. portfolio_manager.py → JSON files
7. api_integration.py → FastAPI Backend → Frontend
```

## 🎯 Componentes Principales

### 1. DataFetcher
- Obtiene datos de yfinance
- Precios actuales e históricos
- Información de mercado
- Rendimiento semanal

### 2. PortfolioCalculator
- Valor total del portafolio
- Rendimiento histórico
- Métricas de riesgo
- Ganadores/perdedores
- Distribución de activos

### 3. ChartGenerator
- Gráficos con Plotly
- HTML interactivos
- PNG estáticos
- Sparklines para tablas

### 4. PortfolioManager
- Orquesta todo el flujo
- Genera reportes completos
- Guarda datos en JSON
- API pública para integración

### 5. APIIntegration
- Servicios para FastAPI
- Funciones helper
- Cache de datos
- Actualización de portafolio

## ⚙️ Configuración

Edita `config.py` para personalizar:

- **PORTFOLIO_CONFIG**: Activos del portafolio
- **WATCHLIST**: Activos para seguimiento de mercado
- **TIME_PERIODS**: Periodos disponibles
- **CHART_CONFIG**: Estilos y dimensiones de gráficos
- **OUTPUT_FILES**: Rutas de archivos generados

## 📈 Métricas Calculadas

- **Valor Total**: Suma del valor de todas las posiciones
- **Cambio %**: Variación porcentual del portafolio
- **Retorno Total**: Rendimiento en el periodo
- **Volatilidad**: Desviación estándar anualizada
- **Sharpe Ratio**: Retorno ajustado por riesgo
- **Max Drawdown**: Máxima caída desde pico

## 🌐 Endpoints Sugeridos para Backend

```
GET  /api/portfolio              - Datos completos del portafolio
GET  /api/portfolio/summary      - Resumen rápido
GET  /api/portfolio/assets       - Lista de activos
GET  /api/market                 - Datos de mercado
GET  /api/market/gainers         - Top ganadores
GET  /api/market/losers          - Top perdedores
GET  /api/chart/portfolio        - Gráfico del portafolio
GET  /api/chart/allocation       - Gráfico de distribución
GET  /api/chart/{symbol}         - Gráfico de activo
POST /api/portfolio/asset        - Agregar activo
PUT  /api/portfolio              - Actualizar portafolio
```

## 🔐 Consideraciones

- **Cache**: Los datos se guardan en Supabase Storage (con fallback JSON local) para evitar llamadas excesivas a la API
- **Rate Limiting**: yfinance tiene límites, usar `force_refresh=False` cuando sea posible
- **Errores**: Manejo robusto de errores con logging
- **Performance**: Los gráficos PNG requieren `kaleido` (opcional)

## 🛠️ Troubleshooting

### Error: "No se pudo guardar PNG"
```bash
pip install kaleido
```

### Error: "No se encontraron datos para SYMBOL"
- Verificar que el símbolo sea correcto
- Verificar conexión a internet
- Revisar si el mercado está abierto

### Performance lento
- Reducir el número de activos
- Usar periodos más cortos
- Activar cache (`force_refresh=False`)

## 📝 TODO

- [ ] Agregar soporte para múltiples portafolios
- [ ] Implementar alertas de precio
- [ ] Agregar backtesting
- [ ] Optimización de portafolio (frontera eficiente)
- [ ] Rebalanceo automático
- [ ] Integración con bases de datos
- [ ] Dashboard en tiempo real

## 📄 Licencia

Este módulo es parte del proyecto Portfolio Manager.

## 👥 Contribuciones

Para agregar nuevas funcionalidades o mejorar el código, seguir la estructura modular existente. 

# GUÍA DE INICIO RÁPIDO - Portfolio Manager

## 📦 Instalación

### Windows

```bash
cd "Portfolio manager"
install.bat
```

O manualmente:

```bash
pip install -r requirements.txt
python test_setup.py
```

### Linux/Mac

```bash
cd "Portfolio manager"
pip install -r requirements.txt
python test_setup.py
```

## 🚀 Uso Rápido

### 1. Generar Reporte Completo

```bash
python portfolio_manager.py
```

Esto generará:
- `data/portfolio_data.json` - Datos completos
- `charts/portfolio_chart.html` - Gráfico interactivo
- `charts/portfolio_chart.png` - Imagen estática
- `charts/assets/` - Gráficos por activo

### 2. Configurar tu Portafolio

Edita `config.py`:

```python
PORTFOLIO_CONFIG = {
    "assets": [
        {"symbol": "AAPL", "units": 10, "name": "Apple"},
        {"symbol": "TSLA", "units": 20, "name": "Tesla"},
        # Agrega tus activos aquí
    ]
}
```

### 3. Personalizar Watchlist

Edita `config.py`:

```python
WATCHLIST = [
    {"symbol": "SPOT", "name": "Spotify", "exchange": "NYSE"},
    {"symbol": "NVDA", "name": "NVIDIA", "exchange": "NASDAQ"},
    # Agrega activos para seguir
]
```

## 🔌 Integración con Backend

### FastAPI

Copia `portfolio_api_example.py` a tu backend y ejecuta:

```bash
cd mi-proyecto-backend
python portfolio_api_example.py
```

Accede a:
- http://localhost:8000/docs - Documentación Swagger
- http://localhost:8000/api/portfolio - Datos del portafolio
- http://localhost:8000/api/market - Datos de mercado

### Endpoints Principales

```
GET  /api/portfolio              - Datos completos
GET  /api/portfolio/summary      - Resumen rápido
GET  /api/market                 - Datos de mercado
GET  /api/chart/portfolio        - Gráfico HTML
```

## 📊 Usar en Frontend

### Obtener Datos

```javascript
// Obtener resumen del portafolio
const response = await fetch('http://localhost:8000/api/portfolio/summary');
const portfolio = await response.json();

console.log(`Valor: $${portfolio.total_value}`);
console.log(`Cambio: ${portfolio.total_change_percent}%`);
```

### Mostrar Gráfico

```html
<!-- Incrustar gráfico en iframe -->
<iframe 
  src="http://localhost:8000/api/chart/portfolio" 
  width="100%" 
  height="400px"
  frameborder="0">
</iframe>
```

O usando fetch:

```javascript
const response = await fetch('http://localhost:8000/api/chart/portfolio');
const html = await response.text();
document.getElementById('chart-container').innerHTML = html;
```

## 🛠️ Comandos Útiles

### Verificar Instalación

```bash
python test_setup.py
```

### Generar Solo Datos (sin gráficos)

```python
from portfolio_manager import PortfolioManager
manager = PortfolioManager()
summary = manager.get_portfolio_summary()
print(summary)
```

### Actualizar Datos

```python
from api_integration import portfolio_service

# Forzar actualización
data = portfolio_service.get_portfolio_data(force_refresh=True)
```

## 📝 Personalización

### Cambiar Colores de Gráficos

Edita `config.py`:

```python
CHART_CONFIG = {
    "colors": {
        "positive": "#10b981",  # Verde
        "negative": "#ef4444",  # Rojo
        "neutral": "#3b82f6",   # Azul
    }
}
```

### Cambiar Periodos

Edita `config.py`:

```python
TIME_PERIODS = {
    "1D": "1d",
    "1W": "1wk",
    "1M": "1mo",
    "6M": "6mo",
    "1Y": "1y",
}
```

## 🐛 Solución de Problemas

### Error: Module not found

```bash
pip install -r requirements.txt
```

### Error: No se pueden guardar PNG

```bash
pip install kaleido
```

### Error: No data found

- Verifica tu conexión a internet
- Verifica que los símbolos sean correctos
- Espera a que el mercado abra

### Datos desactualizados

```python
# Forzar actualización
manager.generate_full_report(period="6mo")
```

## 📚 Estructura de Datos

### Portfolio Summary

```json
{
  "total_value": 12304.11,
  "total_change_percent": 3.65,
  "total_change_absolute": 5.30,
  "assets": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "units": 10,
      "current_price": 172.13,
      "position_value": 1721.30,
      "change_percent": 0.45,
      "change_absolute": 7.73
    }
  ],
  "timestamp": "2025-10-05T..."
}
```

### Market Data

```json
{
  "all": [...],
  "gainers": [...],
  "losers": [...],
  "most_viewed": [...]
}
```

## 🎯 Próximos Pasos

1. ✅ Instalar dependencias
2. ✅ Ejecutar test_setup.py
3. ✅ Configurar portafolio en config.py
4. ✅ Generar primer reporte
5. ✅ Integrar con backend
6. ✅ Conectar con frontend

## 💡 Tips

- **Cache**: Los datos se guardan en JSON para evitar llamadas excesivas
- **Rate Limiting**: yfinance tiene límites, usar cache cuando sea posible
- **Performance**: Reducir número de activos si es lento
- **Actualización**: Usar `force_refresh=False` para datos cacheados

## 📖 Más Información

Ver `README.md` para documentación completa.

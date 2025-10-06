# 🔗 GUÍA DE INTEGRACIÓN CON FRONTEND

## Resumen

Este documento explica cómo integrar el Portfolio Manager con el frontend de tu aplicación.

---

## 📋 Pre-requisitos

1. ✅ Portfolio Manager instalado y funcionando
2. ✅ Backend FastAPI ejecutándose
3. ✅ Frontend con capacidad de hacer peticiones HTTP

---

## 🚀 PASO 1: Iniciar el Backend

```bash
cd mi-proyecto-backend
python portfolio_api_example.py
```

El servidor estará disponible en: `http://localhost:8000`

Documentación Swagger: `http://localhost:8000/docs`

---

## 🔌 PASO 2: Endpoints Disponibles

### Portfolio

```javascript
// Obtener datos completos del portafolio
GET /api/portfolio?period=6mo&refresh=false

// Obtener resumen rápido
GET /api/portfolio/summary

// Obtener lista de activos
GET /api/portfolio/assets

// Agregar un activo
POST /api/portfolio/asset
Body: { "symbol": "NVDA", "units": 5 }

// Actualizar portafolio completo
PUT /api/portfolio
Body: [
  { "symbol": "AAPL", "units": 10, "name": "Apple" },
  { "symbol": "TSLA", "units": 20, "name": "Tesla" }
]
```

### Market

```javascript
// Obtener datos de mercado (watchlist)
GET /api/market

// Obtener top ganadores
GET /api/market/gainers

// Obtener top perdedores
GET /api/market/losers
```

### Charts

```javascript
// Gráfico del portafolio
GET /api/chart/portfolio

// Gráfico de distribución
GET /api/chart/allocation

// Gráfico de un activo
GET /api/chart/AAPL
```

---

## 💻 PASO 3: Código Frontend

### A. Servicio de API (JavaScript/TypeScript)

```typescript
// portfolioService.ts

const API_BASE_URL = 'http://localhost:8000/api';

export const portfolioService = {
  // Obtener resumen del portafolio
  async getPortfolioSummary() {
    const response = await fetch(`${API_BASE_URL}/portfolio/summary`);
    if (!response.ok) throw new Error('Error obteniendo resumen');
    return response.json();
  },

  // Obtener datos completos
  async getPortfolioData(period = '6mo', refresh = false) {
    const response = await fetch(
      `${API_BASE_URL}/portfolio?period=${period}&refresh=${refresh}`
    );
    if (!response.ok) throw new Error('Error obteniendo datos');
    return response.json();
  },

  // Obtener datos de mercado
  async getMarketData() {
    const response = await fetch(`${API_BASE_URL}/market`);
    if (!response.ok) throw new Error('Error obteniendo datos de mercado');
    return response.json();
  },

  // Agregar activo
  async addAsset(symbol, units) {
    const response = await fetch(`${API_BASE_URL}/portfolio/asset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, units })
    });
    if (!response.ok) throw new Error('Error agregando activo');
    return response.json();
  },

  // Obtener HTML de gráfico
  async getChartHTML(chartType) {
    const response = await fetch(`${API_BASE_URL}/chart/${chartType}`);
    if (!response.ok) throw new Error('Error obteniendo gráfico');
    return response.text();
  }
};
```

### B. Componente Total Holding (React)

```jsx
// TotalHoldingCard.jsx

import { useEffect, useState } from 'react';
import { portfolioService } from './portfolioService';

export function TotalHoldingCard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    // Actualizar cada 5 minutos
    const interval = setInterval(loadData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const summary = await portfolioService.getPortfolioSummary();
      setData(summary);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando...</div>;
  if (!data) return <div>Sin datos</div>;

  const isPositive = data.total_change_percent >= 0;

  return (
    <div className="total-holding-card">
      <div className="holding-header">
        <span>Total Holding</span>
      </div>
      <div className="holding-amount">
        ${data.total_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
      </div>
      <div className="holding-return">
        <span>Return</span>
        <span className={isPositive ? 'positive' : 'negative'}>
          {isPositive ? '↑' : '↓'} {Math.abs(data.total_change_percent).toFixed(2)}%
        </span>
        <span className="absolute-change">
          (${Math.abs(data.total_change_absolute).toFixed(2)})
        </span>
      </div>
    </div>
  );
}
```

### C. Carrusel de Activos (React)

```jsx
// PortfolioCarousel.jsx

import { useEffect, useState } from 'react';
import { portfolioService } from './portfolioService';

export function PortfolioCarousel() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAssets();
  }, []);

  const loadAssets = async () => {
    try {
      const data = await portfolioService.getPortfolioSummary();
      setAssets(data.assets || []);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando activos...</div>;

  return (
    <div className="carousel-container">
      <div className="cards-carousel">
        {assets.map((asset) => (
          <AssetCard key={asset.symbol} asset={asset} />
        ))}
      </div>
    </div>
  );
}

function AssetCard({ asset }) {
  const isPositive = asset.change_percent >= 0;

  return (
    <div className="stock-card">
      <div className="stock-price">
        ${asset.current_price.toFixed(2)}
      </div>
      <div className={`stock-change ${isPositive ? 'positive' : 'negative'}`}>
        {isPositive ? '↑' : '↓'} {Math.abs(asset.change_percent).toFixed(2)}%
      </div>
      <div className="stock-info">
        <div className="stock-logo-symbol">
          <span className="stock-symbol">{asset.symbol}</span>
        </div>
        <div className="stock-units">UNITS {asset.units}</div>
      </div>
    </div>
  );
}
```

### D. Gráfico de Rendimiento (React)

```jsx
// PortfolioChart.jsx

import { useEffect, useState, useRef } from 'react';
import { portfolioService } from './portfolioService';

export function PortfolioChart() {
  const containerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('6mo');

  useEffect(() => {
    loadChart();
  }, [period]);

  const loadChart = async () => {
    try {
      // Primero generar datos con el periodo seleccionado
      await portfolioService.getPortfolioData(period, true);
      
      // Luego cargar el HTML del gráfico
      const chartHTML = await portfolioService.getChartHTML('portfolio');
      
      if (containerRef.current) {
        containerRef.current.innerHTML = chartHTML;
      }
    } catch (error) {
      console.error('Error cargando gráfico:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-header">
        <h2>Rendimiento del Portafolio</h2>
        <div className="period-buttons">
          {['1d', '1wk', '1mo', '6mo', '1y'].map((p) => (
            <button
              key={p}
              className={period === p ? 'active' : ''}
              onClick={() => setPeriod(p)}
            >
              {p.toUpperCase()}
            </button>
          ))}
        </div>
      </div>
      
      {loading ? (
        <div className="chart-skeleton">Cargando gráfico...</div>
      ) : (
        <div ref={containerRef} className="chart-content" />
      )}
    </div>
  );
}
```

### E. Tabla de Resumen de Cartera (React)

```jsx
// PortfolioOverview.jsx

import { useEffect, useState } from 'react';
import { portfolioService } from './portfolioService';

export function PortfolioOverview() {
  const [data, setData] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'gainers', 'losers'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const portfolioData = await portfolioService.getPortfolioData();
      setData(portfolioData);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando...</div>;
  if (!data) return <div>Sin datos</div>;

  const getFilteredAssets = () => {
    if (filter === 'gainers') return data.gainers;
    if (filter === 'losers') return data.losers;
    return data.assets;
  };

  const assets = getFilteredAssets();

  return (
    <div className="portfolio-overview">
      <div className="overview-header">
        <h2>Resumen de cartera</h2>
        <div className="filter-buttons">
          <button
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            Todos
          </button>
          <button
            className={filter === 'gainers' ? 'active' : ''}
            onClick={() => setFilter('gainers')}
          >
            Ganadores
          </button>
          <button
            className={filter === 'losers' ? 'active' : ''}
            onClick={() => setFilter('losers')}
          >
            Perdedores
          </button>
        </div>
      </div>

      <table className="overview-table">
        <thead>
          <tr>
            <th>Activo</th>
            <th align="right">Últ. Precio</th>
            <th align="right">Cambio</th>
            <th align="right">Cap. Mercado</th>
            <th align="right">Volumen</th>
          </tr>
        </thead>
        <tbody>
          {assets.map((asset) => (
            <tr key={asset.symbol}>
              <td>
                <div className="stock-cell">
                  <span>{asset.symbol}</span>
                </div>
              </td>
              <td align="right">${asset.current_price.toFixed(2)}</td>
              <td
                align="right"
                className={asset.change_percent >= 0 ? 'positive' : 'negative'}
              >
                {asset.change_percent >= 0 ? '+' : ''}
                {asset.change_percent.toFixed(2)}%
              </td>
              <td align="right">
                {asset.market_cap
                  ? `$${(asset.market_cap / 1e9).toFixed(1)}B`
                  : 'N/A'}
              </td>
              <td align="right">
                {asset.volume
                  ? `${(asset.volume / 1e6).toFixed(1)}M`
                  : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### F. Watchlist (React)

```jsx
// Watchlist.jsx

import { useEffect, useState } from 'react';
import { portfolioService } from './portfolioService';

export function Watchlist() {
  const [data, setData] = useState(null);
  const [tab, setTab] = useState('most_viewed'); // 'most_viewed', 'gainers', 'losers'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    // Actualizar cada 5 minutos
    const interval = setInterval(loadData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const marketData = await portfolioService.getMarketData();
      setData(marketData);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando watchlist...</div>;
  if (!data) return <div>Sin datos</div>;

  const getCurrentList = () => {
    if (tab === 'gainers') return data.gainers;
    if (tab === 'losers') return data.losers;
    return data.most_viewed;
  };

  const items = getCurrentList();

  return (
    <div className="watchlist-container">
      <div className="watchlist-header">
        <h2>Watchlist</h2>
        <div className="watchlist-tabs">
          <button
            className={tab === 'most_viewed' ? 'active' : ''}
            onClick={() => setTab('most_viewed')}
          >
            Most Viewed
          </button>
          <button
            className={tab === 'gainers' ? 'active' : ''}
            onClick={() => setTab('gainers')}
          >
            Gainers
          </button>
          <button
            className={tab === 'losers' ? 'active' : ''}
            onClick={() => setTab('losers')}
          >
            Losers
          </button>
        </div>
      </div>

      <div className="watchlist-items">
        {items.map((item) => (
          <WatchlistItem key={item.symbol} item={item} />
        ))}
      </div>
    </div>
  );
}

function WatchlistItem({ item }) {
  const isPositive = item.change_percent >= 0;

  return (
    <div className="watchlist-item">
      <div className="item-info">
        <div className="item-name">{item.name}</div>
        <div className="item-exchange">{item.exchange} {item.symbol}</div>
      </div>
      <div className="item-price-container">
        <div className="item-price">${item.current_price?.toFixed(2) || 'N/A'}</div>
        <div className={`item-change ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? '↑' : '↓'} {Math.abs(item.change_percent).toFixed(2)}%
        </div>
      </div>
    </div>
  );
}
```

---

## 🎨 PASO 4: Estilos CSS

```css
/* Estilos básicos para los componentes */

.total-holding-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.holding-amount {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 16px 0;
}

.positive {
  color: #10b981;
}

.negative {
  color: #ef4444;
}

.stock-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  min-width: 180px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.chart-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.overview-table {
  width: 100%;
  border-collapse: collapse;
}

.overview-table th,
.overview-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.watchlist-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.watchlist-item {
  display: flex;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid #e5e7eb;
}
```

---

## 🔄 PASO 5: Auto-Refresh

```javascript
// useAutoRefresh.js - Custom Hook

import { useEffect, useRef } from 'react';

export function useAutoRefresh(callback, interval = 5 * 60 * 1000) {
  const savedCallback = useRef();

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    function tick() {
      savedCallback.current();
    }

    // Ejecutar inmediatamente
    tick();

    // Configurar intervalo
    const id = setInterval(tick, interval);
    return () => clearInterval(id);
  }, [interval]);
}

// Uso:
function MyComponent() {
  const [data, setData] = useState(null);

  useAutoRefresh(async () => {
    const newData = await portfolioService.getPortfolioSummary();
    setData(newData);
  }, 5 * 60 * 1000); // 5 minutos

  return <div>{/* ... */}</div>;
}
```

---

## ⚡ PASO 6: Loading States

```jsx
// SkeletonLoader.jsx

export function SkeletonLoader({ type = 'card' }) {
  if (type === 'card') {
    return (
      <div className="skeleton-card animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-12 bg-gray-200 rounded w-full mb-2"></div>
        <div className="h-6 bg-gray-200 rounded w-1/2"></div>
      </div>
    );
  }

  if (type === 'table') {
    return (
      <div className="skeleton-table animate-pulse">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 bg-gray-200 rounded mb-2"></div>
        ))}
      </div>
    );
  }

  return null;
}

// CSS para animación
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

---

## 🐛 PASO 7: Error Handling

```javascript
// ErrorBoundary.jsx

import React from 'react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error capturado:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-container">
          <h2>Algo salió mal</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Recargar página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Uso:
<ErrorBoundary>
  <PortfolioCarousel />
</ErrorBoundary>
```

---

## ✅ CHECKLIST DE INTEGRACIÓN

- [ ] Backend FastAPI ejecutándose
- [ ] Configurar CORS en backend
- [ ] Crear servicio de API en frontend
- [ ] Implementar componente Total Holding
- [ ] Implementar carrusel de activos
- [ ] Implementar gráfico de rendimiento
- [ ] Implementar tabla de resumen
- [ ] Implementar watchlist
- [ ] Agregar auto-refresh
- [ ] Agregar loading states
- [ ] Agregar error handling
- [ ] Probar en diferentes navegadores
- [ ] Optimizar performance

---

## 🎯 PRÓXIMOS PASOS

1. Implementar los componentes en tu framework (React/Vue/Angular)
2. Ajustar estilos según tu diseño
3. Agregar interacciones adicionales (tooltips, modals, etc.)
4. Implementar autenticación si es necesario
5. Optimizar para mobile
6. Agregar tests

---

## 📚 RECURSOS ADICIONALES

- Documentación API: http://localhost:8000/docs
- README Portfolio Manager: `Portfolio manager/README.md`
- Guía Rápida: `Portfolio manager/QUICK_START.md`
- Resumen Implementación: `Portfolio manager/IMPLEMENTATION_SUMMARY.md`

---

¡Listo para integrar! 🚀

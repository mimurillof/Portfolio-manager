# ✅ CORRECCIONES APLICADAS - 17 de Octubre 2025

## Resumen Ejecutivo

Se han aplicado 3 correcciones críticas al sistema Portfolio Manager:

---

## 1. ✅ BUCLE DE WORKER - CORRECTO (NO REQUIERE CAMBIOS)

### ¿Qué hace?
El worker ejecuta `generate_report.py` cada **15 minutos** solo durante horario de mercado (NYSE):
- **Horario:** Lunes a Viernes, 9:30 AM - 4:00 PM ET
- **Fuera de horario:** El worker sigue corriendo pero **NO ejecuta** la generación

### ¿Por qué es importante?

1. **Datos en tiempo real**: Los precios de acciones cambian constantemente durante horario de mercado
2. **Reportes actualizados**: Cada 15 minutos se regeneran los reportes con datos frescos
3. **Eficiencia**: No consume recursos fuera de horario cuando el mercado está cerrado
4. **Escalabilidad**: Procesa automáticamente todos los usuarios en cada ciclo

### Comportamiento esperado:

**Durante horario de mercado (9:30 AM - 4:00 PM ET):**
```
09:30 → Genera reportes
09:45 → Genera reportes
10:00 → Genera reportes
...
16:00 → Genera reportes (última ejecución)
```

**Fuera de horario:**
```
16:15 → "⊘ Fuera de horario de mercado. Saltando ejecución."
16:30 → "⊘ Fuera de horario de mercado. Saltando ejecución."
...
```

### Código relevante:
```python
def is_market_hours():
    """Verifica si estamos en horario de mercado (NYSE)"""
    ny_tz = pytz.timezone('America/New_York')
    now = datetime.now(ny_tz)
    
    if now.weekday() > 4:  # Sábado o Domingo
        return False
    
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)
    
    return market_open <= now <= market_close

def run_worker(period="6mo", skip_empty=True):
    """Ejecuta el worker cada 15 minutos durante horario de mercado"""
    schedule.every(15).minutes.do(scheduled_task)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
```

**Conclusión:** Este comportamiento es **CORRECTO y debe mantenerse**. No se realizaron cambios.

---

## 2. ✅ ESTRUCTURA DE CARPETAS - CORREGIDA

### Problema Original:
Se creaban subcarpetas innecesarias:
```
portfolio-files/
└── {user_id}/
    ├── Informes/          ← NO NECESARIA
    │   └── portfolio_data.json
    └── Graficos/          ← NO NECESARIA
        └── allocation_chart.html
```

### Corrección Aplicada:
Estructura **plana** sin subcarpetas:
```
portfolio-files/
└── {user_id}/
    ├── portfolio_data.json
    ├── portfolio_chart.html
    ├── allocation_chart.html
    ├── drawdown_underwater.html
    └── asset_AAPL_chart.html
```

### Archivos modificados:

**`config.py`** - 4 cambios:

1. **`portfolio_json_path()`** (línea ~66):
```python
# ANTES
return f"{user_id}/Informes/{cls.SUPABASE_PORTFOLIO_FILENAME}".strip("/")

# DESPUÉS
return f"{user_id}/{cls.SUPABASE_PORTFOLIO_FILENAME}".strip("/")
```

2. **`charts_prefix()`** (línea ~87):
```python
# ANTES
return f"{user_id}/Graficos"

# DESPUÉS
return f"{user_id}"
```

3. **`build_chart_path()`** (línea ~100):
```python
# ANTES
relative_clean = relative_path.strip("/")
prefix = cls.charts_prefix(user_id)
if prefix:
    return f"{prefix}/{relative_clean}".strip("/")

# DESPUÉS
from pathlib import Path as PathLib
filename = PathLib(relative_path).name  # Solo nombre de archivo
prefix = cls.charts_prefix(user_id)
if prefix:
    return f"{prefix}/{filename}".strip("/")
```

4. **`remote_chart_path_for()`** (línea ~120):
```python
# ANTES
try:
    relative = local_path.relative_to(CHARTS_DIR)
except ValueError:
    relative = local_path.name
...

# DESPUÉS
filename = local_path.name  # Simplificado
return cls.build_chart_path(filename, user_id)
```

---

## 3. ✅ ALLOCATION_CHART CON DATOS DINÁMICOS - CORREGIDA

### Problema Original:
El gráfico `allocation_chart.html` podría estar recalculando los assets en lugar de usar los datos dinámicos del usuario.

### Causa Raíz:
En `portfolio_manager.py`, el método `_generate_charts()` recalculaba `allocation`:
```python
# ANTES (línea 270)
allocation = self.calculator.calculate_asset_allocation(assets_data)
```

Esto podría causar inconsistencias si `assets_data` difiere de los assets calculados en `generate_full_report()`.

### Corrección Aplicada:
**Archivo:** `portfolio_manager.py` - 2 cambios

1. **Actualizar firma de `_generate_charts()`** (línea ~190):
```python
# ANTES
def _generate_charts(
    self, 
    performance_df, 
    assets_data: List[Dict],
    user_id: Optional[str] = None
) -> Dict[str, str]:

# DESPUÉS
def _generate_charts(
    self, 
    performance_df, 
    assets_data: List[Dict],
    allocation: List[Dict],  # Parámetro nuevo
    user_id: Optional[str] = None
) -> Dict[str, str]:
```

2. **Pasar allocation desde generate_full_report()** (línea ~155):
```python
# ANTES
generated_chart_paths = self._generate_charts(
    performance_df, 
    portfolio_summary["assets"], 
    user_id
)

# DESPUÉS
generated_chart_paths = self._generate_charts(
    performance_df, 
    portfolio_summary["assets"], 
    allocation,  # Pasar allocation ya calculado
    user_id
)
```

3. **Eliminar recálculo en _generate_charts()** (línea ~270):
```python
# ANTES
allocation = self.calculator.calculate_asset_allocation(assets_data)
allocation_html = Path(...) / "allocation_chart.html"
...

# DESPUÉS
# Usar allocation pasado como parámetro (sin recalcular)
allocation_html = Path(...) / "allocation_chart.html"
self.chart_generator.create_allocation_pie_chart(
    allocation,  # Usa el parámetro
    allocation_html,
    allocation_png
)
```

### Beneficios:
1. ✅ **Consistencia**: allocation_chart usa los mismos datos que el reporte JSON
2. ✅ **Performance**: Se calcula solo una vez en lugar de dos veces
3. ✅ **Garantía**: allocation_chart refleja exactamente los assets del usuario

---

## 📋 VALIDACIÓN POST-CORRECCIONES

### Ejecutar script de verificación:
```bash
cd "Portfolio manager"
python verify_fixes.py
```

Este script verifica:
- ✓ Estructura de carpetas plana (sin Informes/ o Graficos/)
- ✓ Allocation se pasa como parámetro (no se recalcula)
- ✓ Worker loop implementado correctamente

### Prueba end-to-end:
```bash
python generate_report.py --verbose
```

**Verificar en logs:**
```
✓ INFO:supabase_client: Usuarios encontrados: X
✓ INFO:ticker_normalizer: Ticker normalizado: BTCUSD → BTC-USD
✓ INFO:portfolio_processor: ✓ Usuario xxx procesado exitosamente

✗ Si ves "Usando configuración hardcodeada" → Hay un problema
```

### Verificar en Supabase Storage:

Abrir: Dashboard → Storage → `portfolio-files`

**Estructura esperada:**
```
portfolio-files/
├── user-id-1/
│   ├── portfolio_data.json
│   ├── portfolio_chart.html
│   ├── allocation_chart.html
│   └── asset_AAPL_chart.html
├── user-id-2/
│   ├── portfolio_data.json
│   └── ...
```

**NO debe haber carpetas `Informes/` o `Graficos/`**

### Verificar allocation_chart:

1. Descargar `allocation_chart.html` desde Storage
2. Abrir en navegador
3. Verificar que muestra los **assets del usuario**, NO los hardcodeados (AAPL, TSLA, MSFT, GOOG, AMZN)

---

## 🎯 RESUMEN DE CAMBIOS

| Archivo | Líneas Modificadas | Cambio |
|---------|-------------------|--------|
| `config.py` | ~66, ~87, ~100, ~120 | Eliminar subcarpetas Informes/ y Graficos/ |
| `portfolio_manager.py` | ~155, ~190, ~270 | Pasar allocation calculado a _generate_charts() |

**Total:** 2 archivos, 7 cambios

---

## ✅ ESTADO FINAL

- ✅ **Bucle de worker**: Correcto (sin cambios)
- ✅ **Estructura plana**: Corregida (sin subcarpetas)
- ✅ **Allocation dinámico**: Corregida (sin recalcular)

**Sistema listo para testing y deployment.**

---

**Próximo paso:** Ejecutar `python verify_fixes.py` para validar las correcciones.

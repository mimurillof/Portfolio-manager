# Guía de Migración: Sistema Multi-Cliente Portfolio Manager

## 📋 Resumen de Cambios

Este documento describe la transformación del Portfolio Manager de un sistema de **usuario único hardcodeado** a un sistema **multi-cliente dinámico** que lee datos desde Supabase.

---

## 🎯 Objetivo de la Migración

**ANTES:** El portafolio estaba hardcodeado en `config.py` con assets estáticos:
```python
PORTFOLIO_CONFIG = {
    "assets": [
        {"symbol": "AAPL", "units": 10, "name": "Apple"},
        {"symbol": "TSLA", "units": 20, "name": "Tesla"},
        # ...
    ]
}
```

**AHORA:** El sistema lee múltiples clientes desde Supabase, cada uno con sus propios portfolios y assets, generando reportes individuales almacenados en subcarpetas específicas por usuario.

---

## 🏗️ Arquitectura de Datos

### Estructura de la Base de Datos

```
┌─────────────┐
│   users     │
│ (user_id PK)│
└──────┬──────┘
       │ 1:N
       │
┌──────▼──────────┐
│   portfolios    │
│ (portfolio_id PK│
│  user_id FK)    │
└──────┬──────────┘
       │ 1:N
       │
┌──────▼──────────┐
│     assets      │
│ (asset_id PK    │
│  portfolio_id FK│
│  asset_symbol)  │
└─────────────────┘
```

### Estructura de Almacenamiento en Supabase Storage

**ANTES (Legacy):**
```
portfolio-files/
├── Informes/
│   └── portfolio_data.json
└── Graficos/
    ├── portfolio_chart.html
    ├── portfolio_chart.png
    └── assets/
        ├── AAPL_chart.html
        └── TSLA_chart.html
```

**AHORA (Multi-Cliente):**
```
portfolio-files/
├── {user_id_1}/
│   ├── Informes/
│   │   └── portfolio_data.json
│   └── Graficos/
│       ├── portfolio_chart.html
│       ├── portfolio_chart.png
│       └── assets/
│           ├── AAPL_chart.html
│           └── MSFT_chart.html
├── {user_id_2}/
│   ├── Informes/
│   │   └── portfolio_data.json
│   └── Graficos/
│       └── ...
```

---

## 🔧 Cambios en el Código

### 1. Nuevos Módulos

#### `supabase_client.py`
Cliente para realizar queries a las tablas de Supabase.

**Métodos principales:**
- `get_all_users()` - Obtiene todos los usuarios
- `get_user_portfolios(user_id)` - Portfolios de un usuario
- `get_portfolio_assets(portfolio_id)` - Assets de un portfolio
- `get_user_full_data(user_id)` - Datos completos (usuario + portfolios + assets)
- `get_all_users_with_portfolios()` - Todos los usuarios con sus datos completos

#### `portfolio_processor.py`
Orquestador del procesamiento multi-cliente.

**Métodos principales:**
- `process_user(user_id, period)` - Procesa un usuario específico
- `process_all_users(period)` - Procesa todos los usuarios (batch)
- `_transform_assets_format()` - Convierte formato DB → formato PortfolioManager

#### `batch_process_portfolios.py`
Script ejecutable para procesamiento batch.

**Uso:**
```bash
# Procesar todos los usuarios
python batch_process_portfolios.py

# Procesar con periodo específico
python batch_process_portfolios.py --period 1y

# Procesar usuario específico
python batch_process_portfolios.py --user-id UUID

# Omitir usuarios sin assets
python batch_process_portfolios.py --skip-empty

# Modo verbose
python batch_process_portfolios.py --verbose
```

### 2. Módulos Modificados

#### `config.py`
- ✨ **Nuevo:** Métodos aceptan parámetro `user_id` opcional
- `portfolio_json_path(user_id=None)` → Genera rutas dinámicas
- `charts_prefix(user_id=None)` → Prefijos dinámicos
- `build_chart_path(relative_path, user_id=None)` → Rutas completas dinámicas
- `remote_chart_path_for(local_path, user_id=None)` → Mapeo local → remoto

#### `supabase_storage.py`
- ✨ **Nuevo:** Todos los métodos aceptan `user_id` opcional
- `load_portfolio_json(user_id=None)`
- `save_portfolio_json(data, user_id=None)`
- `upload_chart_asset(local_path, user_id=None)`

#### `portfolio_manager.py`
- ✨ **Nuevo:** `generate_full_report()` acepta parámetros dinámicos:
  ```python
  def generate_full_report(
      self, 
      period: str = "6mo",
      assets_data: Optional[List[Dict]] = None,  # ← Datos dinámicos
      user_id: Optional[str] = None              # ← ID del usuario
  ) -> Dict[str, Any]:
  ```
- Métodos internos actualizados:
  - `_generate_charts(..., user_id)`
  - `_save_portfolio_data(..., user_id)`
  - `_upload_chart_if_enabled(..., user_id)`

---

## 🚀 Cómo Ejecutar el Sistema Multi-Cliente

### Requisitos Previos

1. **Configurar variables de entorno** (`.env`):
   ```env
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_ANON_KEY=eyJ...
   SUPABASE_SERVICE_ROLE_KEY=eyJ...  # Opcional pero recomendado
   SUPABASE_BUCKET_NAME=portfolio-files
   ENABLE_SUPABASE_UPLOAD=true
   ```

2. **Datos en Supabase:**
   - Tabla `users` con al menos un usuario
   - Tabla `portfolios` con portfolios asociados
   - Tabla `assets` con assets en los portfolios

### Ejecución

#### Opción 1: Procesar Todos los Usuarios (Recomendado)

```bash
cd "Portfolio manager"
python batch_process_portfolios.py --period 6mo --skip-empty
```

#### Opción 2: Procesar Usuario Específico

```bash
python batch_process_portfolios.py --user-id "550e8400-e29b-41d4-a716-446655440000"
```

#### Opción 3: Modo Legacy (Usuario Único Hardcodeado)

Si no pasas `assets_data` ni `user_id`, el sistema usará `PORTFOLIO_CONFIG`:

```python
from portfolio_manager import PortfolioManager

manager = PortfolioManager()
report = manager.generate_full_report(period="6mo")
# Usa assets hardcodeados y estructura legacy de storage
```

---

## 📊 Formato de Datos

### Formato de Entrada (Base de Datos)

**Tabla `assets`:**
```json
{
  "asset_id": 1,
  "portfolio_id": 10,
  "asset_symbol": "AAPL",
  "quantity": 15.5,
  "acquisition_price": 145.30,
  "acquisition_date": "2024-01-15"
}
```

### Formato Transformado (Internal)

```python
{
  "symbol": "AAPL",
  "units": 15.5,
  "name": "Apple Inc.",  # Obtenido de yfinance
  "acquisition_price": 145.30,
  "acquisition_date": "2024-01-15"
}
```

### Formato de Salida (Reporte JSON)

```json
{
  "generated_at": "2025-10-17T10:30:00",
  "period": "6mo",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "summary": {
    "total_value": 125000.50,
    "total_change_percent": 15.3,
    "total_change_absolute": 16500.00,
    "timestamp": "2025-10-17T10:30:00"
  },
  "assets": [...],
  "charts": {
    "portfolio_performance": "/local/path/chart.html",
    "portfolio_performance_remote": "user_id/Graficos/portfolio_chart.html",
    "portfolio_performance_url": "https://..."
  }
}
```

---

## 🔄 Resumen de Ejecución Batch

El script genera un resumen detallado al finalizar:

```
================================================================================
RESUMEN DE EJECUCIÓN - PROCESAMIENTO BATCH
================================================================================
Inicio:          2025-10-17T10:00:00
Finalización:    2025-10-17T10:15:32
Total usuarios:  25
Exitosos:        23
Errores:         1
Omitidos:        1
================================================================================

DETALLE POR USUARIO:
--------------------------------------------------------------------------------
Usuario ID                               Estado       Portfolios   Assets
--------------------------------------------------------------------------------
550e8400-e29b-41d4-a716-446655440000...  success      2            8
660e8400-e29b-41d4-a716-446655440001...  success      1            5
770e8400-e29b-41d4-a716-446655440002...  skipped      0            0
  └─ Error: Usuario sin portfolios
--------------------------------------------------------------------------------
```

Además, se guarda un archivo JSON: `output/batch_summary_YYYYMMDD_HHMMSS.json`

---

## ⚠️ Compatibilidad Hacia Atrás

El sistema **mantiene compatibilidad** con el modo legacy:

1. Si no pasas `user_id`, se usa la estructura antigua (`SUPABASE_BASE_PREFIX`)
2. Si no pasas `assets_data`, se usa `PORTFOLIO_CONFIG` hardcodeado
3. Las variables `SUPABASE_BASE_PREFIX` y `SUPABASE_BASE_PREFIX2` siguen funcionando

---

## 🧪 Testing

### Probar con Usuario Individual

```python
from portfolio_processor import PortfolioProcessor

processor = PortfolioProcessor()
result = processor.process_user(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    period="1mo"
)
print(result)
```

### Verificar Estructura de Storage

```python
from supabase_client import SupabaseDBClient

client = SupabaseDBClient()
users = client.get_all_users()
print(f"Total usuarios: {len(users)}")

for user in users:
    print(f"\nUsuario: {user['first_name']} {user['last_name']}")
    portfolios = client.get_user_portfolios(user['user_id'])
    print(f"  Portfolios: {len(portfolios)}")
```

---

## 🐛 Troubleshooting

### Error: "Supabase no está configurado correctamente"

**Solución:** Verifica que las variables de entorno estén configuradas:
```bash
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY
```

### Error: "No se encontraron usuarios en la base de datos"

**Solución:** Verifica que la tabla `users` tenga datos:
```sql
SELECT * FROM users LIMIT 5;
```

### Los archivos no se suben a Supabase

**Solución:** Verifica:
1. `ENABLE_SUPABASE_UPLOAD=true` en `.env`
2. El bucket `portfolio-files` existe y es público
3. La clave tiene permisos de escritura

### Errores de transformación de assets

**Solución:** Verifica que los assets tengan:
- `asset_symbol` (no null)
- `quantity` (numeric)

```sql
SELECT * FROM assets WHERE asset_symbol IS NULL OR quantity IS NULL;
```

---

## 📈 Mejoras Futuras

1. **Procesamiento paralelo** de usuarios (Threading/AsyncIO)
2. **Cache de datos de mercado** para reducir llamadas a yfinance
3. **Notificaciones** por email al completar procesamiento
4. **Dashboard web** para visualizar progreso en tiempo real
5. **Scheduler** automático (Heroku Scheduler, Cron)

---

## 📝 Notas Adicionales

- **Rendimiento:** El procesamiento de N usuarios toma ~5-10 segundos por usuario
- **Rate Limits:** yfinance tiene límites; considera usar cache o delays
- **Logs:** Los logs detallados se imprimen en consola, considera redirigir a archivo
- **Atomicidad:** Si un usuario falla, los demás continúan procesándose

---

## ✅ Checklist de Migración

- [x] Crear `supabase_client.py` para queries de DB
- [x] Actualizar `config.py` con rutas dinámicas
- [x] Refactorizar `supabase_storage.py` para aceptar `user_id`
- [x] Modificar `portfolio_manager.py` para datos dinámicos
- [x] Crear `portfolio_processor.py` para orquestación
- [x] Crear `batch_process_portfolios.py` como script ejecutable
- [x] Documentar cambios en `.env`
- [x] Crear esta guía de migración
- [ ] Poblar base de datos con usuarios de prueba
- [ ] Ejecutar test con 1 usuario
- [ ] Ejecutar batch completo
- [ ] Validar estructura de storage en Supabase

---

**Fecha de creación:** 17 de octubre de 2025  
**Versión:** 1.0.0  
**Autor:** AIDA (AI Data Architect)

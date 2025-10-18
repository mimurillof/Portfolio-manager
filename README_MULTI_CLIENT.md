# Portfolio Manager - Sistema Multi-Cliente

Sistema dinámico de gestión de portfolios que lee datos desde Supabase y genera reportes individuales por cliente.

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

Crea o actualiza el archivo `.env`:

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_BUCKET_NAME=portfolio-files
ENABLE_SUPABASE_UPLOAD=true
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar Procesamiento

**Opción A: Usando `generate_report.py` (Recomendado para producción)**

```bash
# Procesar todos los usuarios (modo multi-cliente)
python generate_report.py

# Con opciones personalizadas
python generate_report.py --period 1y --skip-empty

# Usuario específico
python generate_report.py --user-id UUID

# Modo worker (scheduler automático)
python generate_report.py --worker
```

**Opción B: Usando `batch_process_portfolios.py` (Ejecución única)**

```bash
# Procesar todos los usuarios
python batch_process_portfolios.py

# Ver ayuda
python batch_process_portfolios.py --help
```

**Opción C: Modo Legacy (datos hardcodeados - DEPRECATED)**

```bash
python generate_report_legacy.py
```

## 📁 Estructura de Archivos

```
Portfolio manager/
├── supabase_client.py          # Cliente para queries a la DB
├── portfolio_processor.py       # Orquestador multi-cliente
├── batch_process_portfolios.py # Script ejecutable
├── portfolio_manager.py         # Generador de reportes (modificado)
├── supabase_storage.py         # Cliente de storage (modificado)
├── config.py                    # Configuración (modificado)
├── MIGRATION_GUIDE.md          # Guía técnica completa
└── README_MULTI_CLIENT.md      # Este archivo
```

## 🎯 Casos de Uso

### Procesar Todos los Usuarios

```bash
python batch_process_portfolios.py --period 6mo --skip-empty
```

**Resultado:**
- Lee todos los usuarios desde `users` table
- Para cada usuario, obtiene sus portfolios y assets
- Genera reporte individual
- Almacena en `{bucket}/{user_id}/Informes/` y `{bucket}/{user_id}/Graficos/`

### Procesar Usuario Específico

```bash
python batch_process_portfolios.py --user-id "550e8400-e29b-41d4-a716-446655440000"
```

### Uso Programático

```python
from portfolio_processor import PortfolioProcessor

processor = PortfolioProcessor()

# Procesar todos
summary = processor.process_all_users(period="1y")
print(f"Exitosos: {summary['successful']}")

# Procesar uno
result = processor.process_user(
    user_id="550e8400-...",
    period="6mo"
)
```

## 📊 Estructura de Datos

### Base de Datos (Input)

```sql
-- Tabla users
user_id       | first_name | last_name | email
uuid (PK)     | varchar    | varchar   | varchar

-- Tabla portfolios  
portfolio_id  | user_id    | portfolio_name
int4 (PK)     | uuid (FK)  | varchar

-- Tabla assets
asset_id      | portfolio_id | asset_symbol | quantity
int4 (PK)     | int4 (FK)    | varchar      | numeric
```

### Storage (Output)

```
portfolio-files/
├── {user_id_1}/
│   ├── Informes/
│   │   └── portfolio_data.json
│   └── Graficos/
│       ├── portfolio_chart.html
│       └── assets/
│           └── AAPL_chart.html
└── {user_id_2}/
    └── ...
```

## 🔧 Opciones de Línea de Comandos

```bash
python batch_process_portfolios.py [OPCIONES]

Opciones:
  --period {1d,5d,1mo,3mo,6mo,1y,2y,5y,ytd,max}
                        Periodo de análisis (default: 6mo)
  
  --skip-empty         Omitir usuarios sin assets
  
  --user-id UUID       Procesar solo un usuario
  
  --verbose            Logging detallado (DEBUG)
  
  --no-summary-file    No guardar archivo de resumen
```

## 📈 Monitoreo y Logs

### Logs en Consola

```
2025-10-17 10:30:00 - INFO - INICIANDO PROCESAMIENTO BATCH
2025-10-17 10:30:05 - INFO - [1/25] Procesando usuario 550e8400...
2025-10-17 10:30:12 - INFO - ✓ Usuario 550e8400 procesado: 2 portfolio(s), 8 asset(s)
...
```

### Archivo de Resumen

Se genera automáticamente en `output/batch_summary_YYYYMMDD_HHMMSS.json`:

```json
{
  "started_at": "2025-10-17T10:00:00",
  "completed_at": "2025-10-17T10:15:32",
  "total_users": 25,
  "successful": 23,
  "errors": 1,
  "skipped": 1,
  "details": [...]
}
```

## ⚡ Características

✅ **Multi-Cliente:** Procesa N usuarios de forma secuencial  
✅ **Datos Dinámicos:** Lee desde Supabase en lugar de hardcoded  
✅ **Almacenamiento Aislado:** Cada usuario tiene su subcarpeta  
✅ **Manejo de Errores:** Si un usuario falla, los demás continúan  
✅ **Logging Detallado:** Seguimiento completo del procesamiento  
✅ **Resumen Ejecutivo:** Estadísticas al finalizar  
✅ **Compatibilidad:** Mantiene modo legacy para un solo usuario  

## 🔄 Modo Legacy (Compatibilidad)

Si necesitas usar el modo antiguo (hardcoded):

```python
from portfolio_manager import PortfolioManager

manager = PortfolioManager()
report = manager.generate_full_report(period="6mo")
# Usa PORTFOLIO_CONFIG y estructura legacy
```

## 🐛 Troubleshooting

### No se encuentran usuarios

**Solución:** Verifica la conexión a Supabase y que la tabla `users` tenga datos.

```python
from supabase_client import SupabaseDBClient
client = SupabaseDBClient()
users = client.get_all_users()
print(len(users))
```

### Los archivos no se suben

**Verificar:**
1. `ENABLE_SUPABASE_UPLOAD=true`
2. Bucket `portfolio-files` existe
3. Permisos de escritura configurados

### Errores de transformación

Verifica que los assets tengan:
- `asset_symbol` ≠ NULL
- `quantity` ≠ NULL

## 📚 Documentación Adicional

- **Guía Técnica Completa:** Ver `MIGRATION_GUIDE.md`
- **Configuración:** Ver `config.py`
- **API Reference:** Ver docstrings en cada módulo

## 🤝 Contribuir

Para agregar nuevas funcionalidades:

1. Mantén la compatibilidad con `user_id=None` (modo legacy)
2. Documenta cambios en `MIGRATION_GUIDE.md`
3. Agrega tests si es posible

## 📝 Notas

- **Rendimiento:** ~5-10 seg/usuario
- **Rate Limits:** yfinance puede limitar; considera delays
- **Concurrencia:** Actualmente secuencial; podría paralelizarse

---

**Versión:** 2.0.0  
**Fecha:** 17 de octubre de 2025

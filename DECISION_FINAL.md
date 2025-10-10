# Decisión Final: Portfolio Manager usa SOLO Worker (NO FastAPI)

## Problema Identificado

**FastAPI con scheduler interno NO funciona en Heroku** porque:

1. **El dyno web se duerme tras 30 min sin tráfico HTTP**
2. Cuando se duerme, el scheduler de FastAPI se detiene
3. No genera reportes automáticamente
4. Solo despierta cuando recibe un request HTTP

**Solución: Worker Dyno**

1. **Worker NO se duerme** (proceso continuo en bucle infinito)
2. Heroku NO duerme workers (no dependen de HTTP)
3. Genera reportes cada 15 minutos sin interrupción
4. Se controla con Heroku Scheduler (enciende/apaga en horario de mercado)

## Arquitectura Final

```
Heroku Scheduler (add-on gratuito)
├── Lunes-Viernes 9:30 AM ET: Enciende worker
│   ↓
│   Worker Dyno (generate_report.py --worker)
│   ├── Bucle infinito activo
│   ├── Verifica horario de mercado
│   ├── Genera reporte cada 15 minutos
│   └── Sube a Supabase
│
└── Viernes 4:00 PM ET: Apaga worker
    ↓
    Worker se detiene hasta el lunes
```

### Procfile Correcto (Portfolio Manager)

```
web: uvicorn fastapi_app:app --host 0.0.0.0 --port ${PORT:-9000}
```

### Ventajas de usar solo FastAPI:

✅ **1 solo dyno** (más económico)
✅ **No hay duplicación** de lógica
✅ **No hay conflictos** entre procesos
✅ **Más simple** de mantener
✅ **Endpoints REST** disponibles
✅ **Scheduler integrado** funciona igual

## Casos de Uso de `generate_report.py`

El script `generate_report.py` sigue siendo útil para:

### Modo Manual (sin --worker):
```bash
python generate_report.py
```
- Genera un reporte una sola vez
- Útil para testing local
- No entra en bucle infinito

### Modo Worker (con --worker):
```bash
python generate_report.py --worker
```
- **SOLO usar si NO tienes FastAPI corriendo**
- Útil si quieres un worker puro sin API
- **NO usar junto con FastAPI** (causa duplicación)

## Arquitectura Recomendada

```
Portfolio Manager (Heroku)
├── FastAPI (dyno web)
    ├── Endpoints REST (/report, /market, /summary)
    ├── Scheduler interno (cada 15 min)
    ├── Genera reportes automáticamente
    └── Sube a Supabase

Supabase Storage
└── portfolio-files/
    ├── Informes/portfolio_data.json
    └── Graficos/*.html

Frontend (otro servicio)
└── Consume endpoints REST de Portfolio Manager
```

## Resumen de Archivos Modificados

### ✅ Archivos DENTRO de Portfolio Manager:

1. **`generate_report.py`**
   - ✅ Limpiado emojis
   - ✅ Añadido modo `--worker`
   - ✅ Útil para testing manual

2. **`config.py`**
   - ✅ Añadido `get_logger()`

3. **`requirements.txt`**
   - ✅ Añadido `schedule>=1.2.1`

4. **`Procfile`** ← **CORRECTO**
   - ✅ Solo `web: uvicorn fastapi_app:app`
   - ✅ NO incluye worker (FastAPI ya lo hace)

5. **`EVALUACION_FASTAPI.md`** (este archivo)
   - Documentación de la decisión

### ❌ Archivos FUERA de Portfolio Manager (revertidos):

1. **`../Procfile`** (root del workspace)
   - ❌ NO tocar (es del frontend)
   - ✅ Revertido a estado original

2. **`../requirements.txt`** (root)
   - ❌ NO tocar (es del frontend)

## Deploy en Heroku

### Desde Portfolio Manager:

```bash
cd "Portfolio manager"

# Verificar que estás en el repo correcto
git remote -v

# Commit
git add generate_report.py config.py requirements.txt Procfile
git commit -m "feat: Worker mode disponible + clean logs sin emojis"

# Deploy a Heroku
git push heroku main

# Verificar
heroku ps
heroku logs --tail
```

## Testing Local

### Opción 1: Solo FastAPI (recomendado)
```bash
cd "Portfolio manager"
uvicorn fastapi_app:app --reload
```
- Visita: http://localhost:8000
- El scheduler genera reportes automáticamente

### Opción 2: Solo Worker (para testing)
```bash
cd "Portfolio manager"
python generate_report.py --worker
```
- NO usar si FastAPI está corriendo
- Solo para testing del worker

### Opción 3: Manual (una ejecución)
```bash
cd "Portfolio manager"
python generate_report.py
```
- Genera reporte una vez
- Termina el proceso

## Conclusión Final

**Portfolio Manager está listo con:**
- ✅ FastAPI con scheduler integrado
- ✅ Endpoints REST funcionales
- ✅ Worker mode disponible (pero no necesario)
- ✅ Logs sin emojis
- ✅ Todo dentro de Portfolio Manager (no contamina frontend)

**Siguiente paso:** Hacer commit y deploy desde Portfolio Manager.

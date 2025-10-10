# Worker de Portfolio Manager - Configuración Completa

## Resumen de Cambios

Se ha convertido el script `generate_report.py` en un **worker continuo** que:

- Se ejecuta en un **bucle infinito**
- Genera reportes **cada 15 minutos**
- Solo durante **horario de mercado** (Lunes-Viernes, 9:30 AM - 4:00 PM ET)
- Sube automáticamente a **Supabase**
- Usa la librería `schedule` para programación precisa
- **Sin emojis** en los logs para mejor compatibilidad

---

## Arquitectura Final

```
HEROKU
├── WEB DYNO (FastAPI)
│   ├── Endpoints REST (/report, /market, /summary)
│   ├── Lee de Supabase o archivos locales
│   └── CORS enabled para frontend
│
└── WORKER DYNO (generate_report.py)
    ├── Bucle infinito
    ├── Ejecuta cada 15 minutos
    ├── Solo durante horario NYSE (9:30 AM - 4:00 PM ET)
    └── Sube reportes a Supabase

SUPABASE Storage
└── portfolio-files/
    ├── Informes/portfolio_data.json
    └── Graficos/*.html

FRONTEND (Vercel)
└── Llama a endpoints FastAPI
```

**Nota Importante:** El frontend llama a FastAPI, NO a Supabase directamente. Por eso necesitamos ambos dynos (web + worker).

---

## 🛠️ Archivos Modificados

### 1. `Portfolio manager/generate_report.py`
- ✅ Añadido función `is_market_hours()` para verificar horario de mercado
- ✅ Añadido función `run_worker()` con bucle infinito usando `schedule`
- ✅ Modificado `main()` para funcionar como tarea programable
- ✅ Añadido soporte para `--worker` flag en CLI
- ✅ Importado `schedule`, `time`, `pytz`, y `get_logger`

### 2. `Portfolio manager/requirements.txt` y `requirements.txt` (root)
- ✅ Añadido `schedule>=1.2.1`
- ✅ `pytz>=2023.3` ya estaba presente

### 3. `Portfolio manager/config.py`
- ✅ Añadido función `get_logger(name)` para logging estructurado
- ✅ Importado módulo `logging`

### 4. `Procfile`
- ✅ Ya estaba configurado correctamente: `worker: cd "Portfolio manager" && python generate_report.py --worker`

---

## 🧪 Pruebas Locales

### Opción 1: Ejecutar una sola vez (modo manual)
```bash
cd "Portfolio manager"
python generate_report.py
```

### Opción 2: Ejecutar en modo worker (bucle infinito)
```bash
cd "Portfolio manager"
python generate_report.py --worker
```

**Salida esperada:**
```
2025-10-10 12:00:00 - __main__ - INFO - 🚀 Worker de Portfolio Manager iniciado
2025-10-10 12:00:00 - __main__ - INFO - ⏰ Configuración: Ejecutar cada 15 minutos durante horario de mercado
2025-10-10 12:00:00 - __main__ - INFO - 🕐 Horario: Lunes-Viernes 9:30 AM - 4:00 PM ET
2025-10-10 12:00:00 - __main__ - INFO - ✅ Estamos en horario de mercado. Generando primer reporte...
================================================================================
📊 GENERADOR DE REPORTE DE PORTFOLIO CON WEB SCRAPING
================================================================================
...
2025-10-10 12:00:00 - __main__ - INFO - ♾️  Entrando en bucle infinito. Presiona Ctrl+C para detener.
```

**Para detener el worker:**
- Presiona `Ctrl+C`

---

## 🚀 Deploy en Heroku

### Paso 1: Commit de cambios
```bash
git add "Portfolio manager/generate_report.py"
git add "Portfolio manager/requirements.txt"
git add "Portfolio manager/config.py"
git add requirements.txt
git add Procfile
git commit -m "feat: Convertir Portfolio Manager en worker continuo con schedule"
```

### Paso 2: Deploy a Heroku
```bash
git push heroku main
```

### Paso 3: Verificar estado del worker
```bash
heroku ps --app portofolio-manager-horizon
```

**Salida esperada:**
```
=== worker (Eco): cd "Portfolio manager" && python generate_report.py --worker (1)
worker.1: up 2025/10/10 12:00:00 -0500 (~ 1m ago)
```

### Paso 4: Ver logs en tiempo real
```bash
heroku logs --tail --app portofolio-manager-horizon --dyno worker
```

**Salida esperada:**
```
2025-10-10T17:00:00.000000+00:00 app[worker.1]: 2025-10-10 12:00:00 - __main__ - INFO - 🚀 Worker de Portfolio Manager iniciado
2025-10-10T17:00:00.000000+00:00 app[worker.1]: 2025-10-10 12:00:00 - __main__ - INFO - ✅ Estamos en horario de mercado. Generando primer reporte...
2025-10-10T17:00:30.000000+00:00 app[worker.1]: ================================================================================
2025-10-10T17:00:30.000000+00:00 app[worker.1]: 📊 GENERADOR DE REPORTE DE PORTFOLIO CON WEB SCRAPING
2025-10-10T17:00:30.000000+00:00 app[worker.1]: ================================================================================
...
2025-10-10T17:01:00.000000+00:00 app[worker.1]: ✅ REPORTE GENERADO EXITOSAMENTE
2025-10-10T17:01:00.000000+00:00 app[worker.1]: 💰 Valor Total: $21,639.95
2025-10-10T17:01:00.000000+00:00 app[worker.1]: 📈 Cambio: -2.12%
2025-10-10T17:01:00.000000+00:00 app[worker.1]: 2025-10-10 12:01:00 - __main__ - INFO - ♾️  Entrando en bucle infinito. Presiona Ctrl+C para detener.
```

---

## 🔧 Configuración de Heroku

### Variables de entorno necesarias:
```bash
heroku config:set SUPABASE_URL="https://tu-proyecto.supabase.co" --app portofolio-manager-horizon
heroku config:set SUPABASE_SERVICE_ROLE_KEY="tu-service-role-key" --app portofolio-manager-horizon
heroku config:set SUPABASE_BUCKET_NAME="portfolio-files" --app portofolio-manager-horizon
heroku config:set ENABLE_SUPABASE_UPLOAD="true" --app portofolio-manager-horizon
```

### Verificar configuración:
```bash
heroku config --app portofolio-manager-horizon
```

---

## 📊 Funcionamiento del Worker

### Lógica de Horario de Mercado:
- **Días válidos:** Lunes (0) a Viernes (4)
- **Horario:** 9:30 AM - 4:00 PM hora de Nueva York (ET)
- **Zona horaria:** `America/New_York` (maneja automáticamente DST)

### Comportamiento:
1. **Al iniciar:**
   - Si está en horario de mercado → Genera reporte inmediatamente
   - Si está fuera de horario → Espera a la siguiente verificación

2. **Cada 15 minutos:**
   - Verifica si está en horario de mercado
   - Si SÍ → Genera reporte y sube a Supabase
   - Si NO → Registra log y espera

3. **Ejecución continua:**
   - El worker nunca termina (bucle infinito)
   - Heroku no lo dormirá porque está constantemente activo
   - Usa `time.sleep(1)` para precisión en la programación

---

## 🐛 Troubleshooting

### Problema: Worker se crashea al iniciar
**Solución:** Verificar que todas las dependencias estén instaladas:
```bash
heroku run "pip list | grep schedule" --app portofolio-manager-horizon
```

### Problema: No genera reportes
**Verificar horario actual:**
```bash
heroku run "python -c 'from datetime import datetime; import pytz; print(datetime.now(pytz.timezone(\"America/New_York\")))'" --app portofolio-manager-horizon
```

### Problema: Error de importación
**Verificar estructura de archivos:**
```bash
heroku run "ls -la 'Portfolio manager'" --app portofolio-manager-horizon
```

---

## ✅ Checklist de Deployment

- [ ] Modificado `generate_report.py` con modo worker
- [ ] Añadido `schedule>=1.2.1` a `requirements.txt`
- [ ] Añadido `get_logger()` a `config.py`
- [ ] Verificado `Procfile` con comando correcto
- [ ] Probado localmente con `--worker` flag
- [ ] Commit de todos los cambios
- [ ] Push a Heroku
- [ ] Verificado estado del worker (`heroku ps`)
- [ ] Verificado logs del worker (`heroku logs --tail`)
- [ ] Confirmado que genera reportes cada 15 minutos
- [ ] Verificado subida a Supabase

---

## 🎯 Próximos Pasos

1. **Hacer commit** de los cambios siguiendo el checklist
2. **Desplegar** a Heroku con `git push heroku main`
3. **Monitorear** los logs durante 30 minutos para confirmar funcionamiento
4. **Verificar** en Supabase que los reportes se están subiendo correctamente

---

## 📝 Notas Importantes

- ⚠️ **El worker consumirá horas de dyno constantemente** (aprox. 720 horas/mes)
- ⚠️ **Plan Eco de Heroku:** 1000 horas gratuitas/mes (suficiente para 1 worker 24/7)
- ✅ **El worker NO se dormirá** porque está en bucle infinito activo
- ✅ **Fuera de horario de mercado** solo consume recursos mínimos (sleep loops)
- ✅ **Logs estructurados** para debugging fácil con timestamps y niveles

---

**Última actualización:** 10 de octubre de 2025

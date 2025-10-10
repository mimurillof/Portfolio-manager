# Configuración de Portfolio Manager Worker con Heroku Scheduler

## Problema Identificado

**FastAPI con scheduler interno NO funciona en Heroku** porque:
- ❌ El dyno web se duerme tras 30 min sin tráfico HTTP
- ❌ Cuando se duerme, el scheduler se detiene
- ❌ No genera reportes automáticamente
- ✅ Solo despierta cuando recibe un request HTTP

**Solución: Worker Dyno**
- ✅ Worker NO se duerme (proceso continuo)
- ✅ Genera reportes cada 15 minutos
- ✅ Combinar con Heroku Scheduler para controlar horario

---

## Arquitectura Final

```
Heroku Scheduler (gratuito)
├── Lunes 9:30 AM ET: heroku ps:scale worker=1
│   ↓
│   Worker Dyno ACTIVO
│   ├── Genera reporte cada 15 minutos
│   └── Sube a Supabase
│
└── Viernes 4:00 PM ET: heroku ps:scale worker=0
    ↓
    Worker Dyno APAGADO
```

---

## Archivos Configurados

### 1. Procfile (Portfolio Manager)
```
worker: python generate_report.py --worker
```
- ✅ Solo worker (NO web)
- ✅ El worker es un proceso continuo que NO se duerme

### 2. generate_report.py
- ✅ Modo `--worker` con bucle infinito
- ✅ Verifica horario de mercado internamente
- ✅ Genera reportes cada 15 minutos
- ✅ Logs sin emojis

---

## Configuración de Heroku Scheduler

### Paso 1: Instalar Heroku Scheduler (Gratuito)

```bash
cd "Portfolio manager"
heroku addons:create scheduler:standard --app portofolio-manager-horizon
```

### Paso 2: Abrir Dashboard del Scheduler

```bash
heroku addons:open scheduler --app portofolio-manager-horizon
```

O manualmente en: https://dashboard.heroku.com/apps/portofolio-manager-horizon/scheduler

### Paso 3: Crear Job para ENCENDER el Worker

**Configuración:**
- **Frequency:** Every day at... (Diario)
- **Time:** 09:30 AM (zona horaria UTC - ajustar según ET)
- **Command:**
  ```bash
  heroku ps:scale worker=1 --app portofolio-manager-horizon
  ```

**Nota sobre zona horaria:**
- Heroku Scheduler usa UTC
- NYSE: 9:30 AM ET = 1:30 PM UTC (horario estándar) o 2:30 PM UTC (horario de verano)
- Ajusta según la época del año

### Paso 4: Crear Job para APAGAR el Worker

**Configuración:**
- **Frequency:** Every day at... (Diario)
- **Time:** 04:00 PM ET (ajustar a UTC)
- **Command:**
  ```bash
  heroku ps:scale worker=0 --app portofolio-manager-horizon
  ```

**Conversión de horarios:**
- 4:00 PM ET = 8:00 PM UTC (horario estándar) o 9:00 PM UTC (horario de verano)

### Paso 5: Verificar que el Worker Solo Corre de Lunes a Viernes

**Opción A: Jobs diarios con lógica interna**
- El worker ya tiene `is_market_hours()` que verifica día de la semana
- Si el scheduler lo enciende el sábado/domingo, el worker no genera reportes
- ✅ **Recomendado**: Más simple

**Opción B: Usar Heroku Scheduler con cron personalizado**
- Heroku Scheduler Standard no soporta días específicos nativamente
- Necesitarías upgrade a plan superior o usar scripts bash

---

## Comandos Útiles

### Ver estado del worker
```bash
heroku ps --app portofolio-manager-horizon
```

**Esperado cuando está corriendo:**
```
=== worker (Eco): python generate_report.py --worker (1)
worker.1: up 2025/10/10 09:30:00 -0500 (~ 1h ago)
```

### Ver logs del worker
```bash
heroku logs --tail --app portofolio-manager-horizon --dyno worker
```

### Encender worker manualmente (testing)
```bash
heroku ps:scale worker=1 --app portofolio-manager-horizon
```

### Apagar worker manualmente
```bash
heroku ps:scale worker=0 --app portofolio-manager-horizon
```

### Ver jobs configurados en Scheduler
```bash
heroku addons:open scheduler --app portofolio-manager-horizon
```

---

## Testing Local

### Probar el worker localmente
```bash
cd "Portfolio manager"
python generate_report.py --worker
```

**Salida esperada:**
```
2025-10-10 12:00:00 - __main__ - INFO - Worker de Portfolio Manager iniciado
2025-10-10 12:00:00 - __main__ - INFO - Configuracion: Ejecutar cada 15 minutos durante horario de mercado
2025-10-10 12:00:00 - __main__ - INFO - Horario: Lunes-Viernes 9:30 AM - 4:00 PM ET
2025-10-10 12:00:00 - __main__ - INFO - Estamos en horario de mercado. Generando primer reporte...
================================================================================
GENERADOR DE REPORTE DE PORTFOLIO CON WEB SCRAPING
================================================================================
...
2025-10-10 12:00:19 - __main__ - INFO - Entrando en bucle infinito. Presiona Ctrl+C para detener.
```

---

## Consumo de Horas Heroku

### Con Heroku Scheduler:

**Ejemplo: Lunes a Viernes, 9:30 AM - 4:00 PM (6.5 horas/día)**
- 6.5 horas/día × 5 días/semana = 32.5 horas/semana
- 32.5 horas/semana × 4.33 semanas/mes ≈ **141 horas/mes**

**Plan Eco gratuito:** 1000 horas/mes
**Consumo:** 141 horas/mes
**Horas restantes:** 859 horas/mes

✅ **Suficiente para el plan gratuito**

---

## Deploy a Heroku

### Desde Portfolio Manager:

```bash
cd "Portfolio manager"

# Verificar cambios
git status

# Commit
git add Procfile generate_report.py config.py requirements.txt
git commit -m "feat: Worker mode sin FastAPI para evitar sleep de Heroku"

# Push a Heroku
git push heroku main

# Escalar el worker (inicialmente apagado)
heroku ps:scale worker=0

# Ver logs
heroku logs --tail
```

---

## Flujo de Trabajo Diario (Automático)

### Lunes 9:30 AM ET
1. Heroku Scheduler ejecuta: `heroku ps:scale worker=1`
2. Worker dyno se enciende
3. Worker verifica que es día laborable y horario de mercado
4. Genera primer reporte inmediatamente
5. Entra en bucle: genera reporte cada 15 minutos

### Durante el día (9:30 AM - 4:00 PM)
- Worker genera reportes cada 15 minutos
- Sube JSON y gráficos a Supabase
- Logs visibles en `heroku logs --tail`

### Viernes 4:00 PM ET
1. Heroku Scheduler ejecuta: `heroku ps:scale worker=0`
2. Worker dyno se apaga
3. No consume horas de dyno hasta el lunes

### Fin de semana
- Worker apagado
- No consume recursos
- No genera reportes

---

## Troubleshooting

### El worker no genera reportes
**Verificar:**
```bash
# 1. ¿Está corriendo?
heroku ps --app portofolio-manager-horizon

# 2. ¿Qué dicen los logs?
heroku logs --tail --app portofolio-manager-horizon --dyno worker

# 3. ¿Es horario de mercado?
python -c "from datetime import datetime; import pytz; print(datetime.now(pytz.timezone('America/New_York')))"
```

### Heroku Scheduler no ejecuta los jobs
**Verificar:**
1. Jobs están configurados en el dashboard
2. Zona horaria correcta (UTC)
3. Comando correcto con `--app` flag
4. Logs del scheduler: `heroku logs --source scheduler`

### Worker consume muchas horas
**Solución:**
- Ajustar horarios en Heroku Scheduler
- Reducir tiempo de ejecución diaria
- El worker solo debe correr durante horario de mercado

---

## Resumen de Configuración

✅ **Procfile:** Solo `worker: python generate_report.py --worker`
✅ **generate_report.py:** Modo worker con bucle infinito
✅ **Heroku Scheduler:** Enciende/apaga worker automáticamente
✅ **Consumo:** ~141 horas/mes (dentro del plan gratuito)
✅ **Sin FastAPI:** Evita el problema del sleep

**Estado:** Listo para deploy y configuración de Heroku Scheduler.

# Portfolio Manager - Deploy Worker a Heroku

## Resumen

Portfolio Manager usa un **worker dyno** (NO web) porque:
- ✅ Worker NO se duerme (Heroku solo duerme dynos web sin tráfico)
- ✅ Genera reportes cada 15 minutos sin interrupción
- ✅ Se controla con Heroku Scheduler (enciende/apaga en horario de mercado)

---

## Archivos Listos

### `Procfile`
```
worker: python generate_report.py --worker
```

### `generate_report.py`
- Modo `--worker` con bucle infinito
- Verifica horario de mercado (Lunes-Viernes, 9:30 AM - 4:00 PM ET)
- Genera reporte cada 15 minutos
- Logs sin emojis

### `config.py`
- Añadido `get_logger()` para logging estructurado

### `requirements.txt`
- Añadido `schedule>=1.2.1`

---

## Deploy

### 1. Commit (desde Portfolio Manager)
```bash
cd "Portfolio manager"
git add Procfile generate_report.py config.py requirements.txt
git commit -m "feat: Worker mode para Heroku sin sleep"
git push heroku main
```

### 2. Escalar Worker (Inicialmente Apagado)
```bash
heroku ps:scale worker=0 --app portofolio-manager-horizon
```

### 3. Configurar Heroku Scheduler

**Instalar add-on (gratuito):**
```bash
heroku addons:create scheduler:standard --app portofolio-manager-horizon
```

**Abrir dashboard:**
```bash
heroku addons:open scheduler --app portofolio-manager-horizon
```

**Crear 2 jobs:**

**Job 1: Encender worker** (Lunes-Viernes 9:30 AM ET)
- Frequency: Every day at...
- Time: 09:30 AM (ajustar a UTC según DST)
- Command: `heroku ps:scale worker=1 --app portofolio-manager-horizon`

**Job 2: Apagar worker** (Viernes 4:00 PM ET)
- Frequency: Every day at...
- Time: 04:00 PM (ajustar a UTC según DST)
- Command: `heroku ps:scale worker=0 --app portofolio-manager-horizon`

**Nota:** Heroku Scheduler usa UTC. Convierte los horarios ET a UTC.

---

## Verificación

### Ver estado del worker
```bash
heroku ps --app portofolio-manager-horizon
```

### Ver logs en tiempo real
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

---

## Consumo de Horas

**Con Heroku Scheduler (Lunes-Viernes, 6.5 hrs/día):**
- ~141 horas/mes
- ✅ Dentro del plan Eco gratuito (1000 horas/mes)

---

## Testing Local

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
REPORTE GENERADO EXITOSAMENTE
2025-10-10 12:00:19 - __main__ - INFO - Entrando en bucle infinito. Presiona Ctrl+C para detener.
```

---

## Documentación Completa

Ver `HEROKU_SCHEDULER_SETUP.md` para instrucciones detalladas sobre configuración de Heroku Scheduler.

---

**Estado:** ✅ Listo para deploy

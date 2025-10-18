# 🚀 PRÓXIMOS PASOS - Sistema Multi-Cliente v2.1

## ✅ Estado Actual

El sistema ha sido completamente refactorizado:
- ✅ Lectura dinámica desde Supabase (usuarios → portfolios → assets)
- ✅ Almacenamiento por `user_id` en Supabase Storage
- ✅ Normalizador de tickers integrado (BTCUSD → BTC-USD, NVD.F → NVDA)
- ✅ Script principal actualizado (`generate_report.py`)
- ✅ Procfile configurado
- ✅ Documentación completa

---

## 🎯 Fase de Testing (AHORA)

### Paso 1: Ejecutar Quick Test

```bash
cd "Portfolio manager"
python quick_test.py
```

**Este script verificará:**
- ✓ Todos los módulos se importan correctamente
- ✓ Normalizador de tickers funciona
- ✓ Archivo `.env` está configurado
- ✓ Conexión a Supabase es exitosa
- ✓ Hay usuarios en la base de datos

### Paso 2: Poblar Base de Datos (si está vacía)

Si `quick_test.py` reporta 0 usuarios:

```bash
python populate_test_data.py --users 5
```

Esto creará:
- 5 usuarios de prueba
- 2-3 portfolios por usuario
- 3-7 assets por portfolio (con tickers reales y algunos mal formateados)

### Paso 3: Ejecutar Test Completo

```bash
python generate_report.py --verbose
```

**Observa el log:**
```
INFO:supabase_client: Obteniendo todos los usuarios...
INFO:supabase_client: Usuarios encontrados: 5
INFO:ticker_normalizer: Ticker normalizado: BTCUSD → BTC-USD
INFO:ticker_normalizer: Ticker normalizado: NVD.F → NVDA
INFO:portfolio_processor: ✓ Usuario test-user-1 procesado exitosamente
```

**Si ves "Usando configuración hardcodeada" → HAY UN PROBLEMA**

### Paso 4: Validar Storage en Supabase

Abre Supabase Dashboard → Storage → `portfolio-files`

**Estructura esperada:**
```
portfolio-files/
├── test-user-1/
│   ├── Informes/
│   │   └── portfolio_data.json
│   └── Graficos/
│       ├── portfolio_chart.html
│       └── drawdown_underwater.html
├── test-user-2/
│   ├── Informes/
│   └── Graficos/
└── ...
```

---

## 🔧 Troubleshooting

### Problema: "Usando configuración hardcodeada"

**Causa:** El script sigue usando el código antiguo

**Solución:**
```bash
# Verifica que Procfile tenga la línea correcta:
cat Procfile
# Debe decir: worker: python generate_report.py --worker --period 6mo --skip-empty
```

### Problema: "Error conectando a Supabase"

**Causa:** Variables de entorno no configuradas

**Solución:**
```bash
# Verifica .env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
SUPABASE_BUCKET_NAME=portfolio-files
ENABLE_SUPABASE_UPLOAD=true
```

### Problema: "No data found for ticker BTCUSD"

**Causa:** El ticker no fue normalizado

**Solución:** Ya está resuelto en `portfolio_processor.py` línea 145-158:
```python
normalized_symbol = TickerNormalizer.normalize(original_symbol)
logger.info(f"Ticker normalizado: {original_symbol} → {normalized_symbol}")
```

---

## 🚀 Fase de Deployment

### Paso 5: Deploy a Heroku

```bash
# Asegúrate de estar en la carpeta raíz del proyecto
cd ..

# Commit de cambios
git add .
git commit -m "feat: Multi-cliente v2.1 con normalización de tickers"

# Push a Heroku
git push heroku main

# Configura variables de entorno
heroku config:set SUPABASE_URL="https://..."
heroku config:set SUPABASE_SERVICE_ROLE_KEY="..."
heroku config:set ENABLE_SUPABASE_UPLOAD=true

# Verifica logs
heroku logs --tail --dyno=worker
```

### Paso 6: Monitorear Ejecución

```bash
# Ver logs en tiempo real
heroku logs --tail

# Deberías ver:
# INFO:portfolio_processor: Procesando usuario: john.doe@example.com
# INFO:ticker_normalizer: Ticker normalizado: BTCUSD → BTC-USD
# INFO:portfolio_processor: ✓ Usuario user-id-123 procesado exitosamente
```

---

## 📊 Verificación Final

### Checklist de Producción

- [ ] `quick_test.py` pasa todos los tests
- [ ] Base de datos tiene usuarios reales (no de prueba)
- [ ] `generate_report.py --verbose` NO muestra "configuración hardcodeada"
- [ ] Logs muestran "Ticker normalizado: X → Y"
- [ ] Supabase Storage tiene carpetas por `user_id`
- [ ] Archivos JSON y HTML se suben correctamente
- [ ] Heroku worker está ejecutándose sin errores
- [ ] Los reportes se generan en horario de mercado (9:30 AM - 4:00 PM ET)

---

## 📚 Documentación de Referencia

- **CHANGELOG_v2.1.md**: Cambios completos de esta versión
- **MIGRATION_GUIDE.md**: Guía técnica completa
- **TICKER_NORMALIZATION.md**: Detalles del normalizador
- **README_MULTI_CLIENT.md**: Guía rápida de uso

---

## 🆘 Comandos de Emergencia

### Revertir a modo legacy (hardcodeado)

```bash
python generate_report_legacy.py --period 6mo
```

### Ver qué usuarios procesará el sistema

```bash
python batch_process_portfolios.py --list-users
```

### Procesar un solo usuario específico

```bash
python generate_report.py --user-id test-user-1 --period 1y
```

### Ver detalles de normalización de tickers

```bash
python -c "from ticker_normalizer import TickerNormalizer; print(TickerNormalizer.KNOWN_CORRECTIONS)"
```

---

## ✨ Siguientes Mejoras (Futuro)

1. **Dashboard de Monitoreo**: Página web para ver estado de procesamiento
2. **Alertas por Email**: Notificaciones cuando un portfolio tiene errores
3. **Cache de Datos**: Redis para evitar llamadas repetidas a yfinance
4. **Reportes Personalizados**: Permitir al usuario elegir período y métricas
5. **API REST**: Endpoints para consultar reportes generados

---

**¡El sistema está listo para testing! Ejecuta `python quick_test.py` para comenzar.**

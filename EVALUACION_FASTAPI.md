# Evaluación: ¿Portfolio Manager necesita FastAPI?

## Contexto Aclarado

**Portfolio Manager** es un repositorio Git SEPARADO del frontend.

```
Workspace (mi-proyecto/)
├── Frontend (Repositorio A - React/Vite)
│   ├── Procfile (para el frontend)
│   ├── src/
│   └── ...
│
└── Portfolio manager/ (Repositorio B - Python Backend)
    ├── .git/ (repositorio separado)
    ├── Procfile (ESTE es el correcto)
    ├── fastapi_app.py
    ├── generate_report.py
    ├── requirements.txt
    └── ...
```

## Análisis de FastAPI en Portfolio Manager

### Endpoints Disponibles:
- `GET /health` - Health check
- `GET /report` - Reporte completo del portfolio
- `GET /summary` - Resumen del portfolio
- `GET /market` - Market overview
- `GET /charts/{chart_name}` - Gráficos individuales

### ¿Quién consume estos endpoints?

**Escenario A: Frontend consume Portfolio Manager directamente**
```
Frontend (Vercel) → Portfolio Manager API (Heroku) → Supabase
```
→ **FastAPI es NECESARIO**

**Escenario B: Frontend consume otro backend que consume Portfolio Manager**
```
Frontend → horizon-backend (Heroku) → Portfolio Manager API → Supabase
```
→ **FastAPI es NECESARIO** (para el backend intermediario)

**Escenario C: Frontend solo lee de Supabase**
```
Frontend → Supabase ← Portfolio Manager (solo escribe)
```
→ **FastAPI NO es necesario** (solo worker)

## Verificación del Config Frontend

```typescript
// src/config/api.ts
BASE_URL: 'https://horizon-backend-316b23e32b8b.herokuapp.com' (producción)
ENDPOINTS: {
    PORTFOLIO_MANAGER_BASE: '/api/portfolio-manager'
}
```

El frontend llama a `horizon-backend`, NO directamente a Portfolio Manager.

## Conclusión

### Opción 1: Portfolio Manager como Servicio API (Recomendado)
**Si otro backend o frontend lo consume:**
- ✅ Mantener FastAPI
- ✅ Tener 2 procesos en Procfile:
  ```
  web: uvicorn fastapi_app:app --host 0.0.0.0 --port ${PORT:-9000}
  worker: python generate_report.py --worker
  ```
- ✅ Worker genera datos, FastAPI los sirve

### Opción 2: Portfolio Manager como Worker Puro
**Si NADIE consume la API:**
- ❌ Eliminar FastAPI
- ✅ Solo worker en Procfile:
  ```
  worker: python generate_report.py --worker
  ```
- ✅ Todo se guarda en Supabase
- ✅ Frontend lee directamente de Supabase

## Preguntas para Decidir

1. **¿El backend `horizon-backend-316b23e32b8b.herokuapp.com` consume los endpoints de Portfolio Manager?**
   - Si SÍ → Mantener FastAPI
   - Si NO → Eliminar FastAPI

2. **¿El frontend lee datos de portfolio desde Supabase directamente?**
   - Si SÍ → No necesitas FastAPI
   - Si NO → Necesitas FastAPI

3. **¿Portfolio Manager se despliega en Heroku como servicio independiente?**
   - Si SÍ → Probablemente necesitas FastAPI
   - Si NO → Solo worker

## Recomendación Actual

Basado en que Portfolio Manager tiene:
- ✅ fastapi_app.py con endpoints bien definidos
- ✅ Scheduler automático en FastAPI
- ✅ CORS configurado para frontend
- ✅ Procfile con proceso web

**Recomendación: MANTENER FastAPI**

Portfolio Manager parece diseñado como un **microservicio API REST** que:
1. Genera reportes automáticamente (scheduler en fastapi_app.py)
2. Expone endpoints para consultar datos
3. Se puede consumir desde cualquier cliente

## Procfile Final Recomendado

```
web: uvicorn fastapi_app:app --host 0.0.0.0 --port ${PORT:-9000}
worker: python generate_report.py --worker
```

**Ventajas:**
- FastAPI sirve los datos generados
- Worker genera reportes cada 15 minutos
- Ambos procesos independientes y escalables

**Nota:** Si confirmas que NADIE consume la API, puedo simplificar a solo worker.

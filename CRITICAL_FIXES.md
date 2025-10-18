# 🔧 CORRECCIONES CRÍTICAS - Portfolio Manager

## Fecha: 17 de octubre de 2025

---

## 🐛 PROBLEMAS IDENTIFICADOS

### 1. **BUCLE DE WORKER DURANTE HORARIO DE MERCADO** ✅

**Estado:** CORRECTO - Funciona como se diseñó

**¿Qué hace?**
```python
schedule.every(15).minutes.do(scheduled_task)

while True:
    schedule.run_pending()
    time.sleep(1)
```

**¿Por qué es importante?**

El worker ejecuta el sistema cada **15 minutos** solo durante el horario de la bolsa (NYSE):
- **Horario:** Lunes a Viernes, 9:30 AM - 4:00 PM ET
- **Razón:** Los precios de las acciones cambian en tiempo real durante este período
- **Beneficio:** Reportes actualizados constantemente con datos frescos

**Ventajas:**
1. ✅ **Datos en tiempo real**: Portafolios actualizados cada 15 min
2. ✅ **Eficiencia**: No ejecuta fuera de horario (ahorra recursos)
3. ✅ **Escalable**: Procesa todos los usuarios automáticamente

**Fuera de horario:**
- El worker sigue corriendo pero **no ejecuta** la generación
- Solo registra: `"⊘ Fuera de horario de mercado. Saltando ejecución."`
- Esto es **correcto y esperado**

**Conclusión:** Este comportamiento es **correcto y debe persistir**.

---

### 2. **ALLOCATION_CHART CON DATOS HARDCODEADOS** ❌

**Estado:** ERROR DETECTADO

**Ubicación:** `portfolio_manager.py` línea 270

**Código problemático:**
```python
# En _generate_charts() línea 270
allocation = self.calculator.calculate_asset_allocation(assets_data)
```

**Problema:**
El método `calculate_asset_allocation()` recibe `assets_data` (que son los datos dinámicos del usuario), PERO el código anterior en línea 114 usa `portfolio_summary["assets"]` que **puede estar usando PORTFOLIO_CONFIG hardcodeado**.

**Causa Raíz:**
En línea 114:
```python
allocation = self.calculator.calculate_asset_allocation(
    portfolio_summary["assets"]  # <-- Esto podría ser hardcodeado
)
```

Mientras que en línea 270:
```python
allocation = self.calculator.calculate_asset_allocation(assets_data)  # <-- Esto es dinámico
```

**Solución:** Verificar que ambas llamadas usen la misma fuente de datos dinámicos.

---

### 3. **ESTRUCTURA DE CARPETAS INCORRECTA** ❌

**Estado:** ERROR EN ARQUITECTURA

**Estructura Actual (INCORRECTA):**
```
portfolio-files/
└── {user_id}/
    ├── Informes/
    │   └── portfolio_data.json
    └── Graficos/
        ├── portfolio_chart.html
        └── allocation_chart.html
```

**Estructura Esperada (CORRECTA):**
```
portfolio-files/
└── {user_id}/
    ├── portfolio_data.json
    ├── portfolio_chart.html
    ├── allocation_chart.html
    ├── drawdown_underwater.html
    └── asset_*.html
```

**Problema en `config.py`:**

Línea 66:
```python
return f"{user_id}/Informes/{cls.SUPABASE_PORTFOLIO_FILENAME}".strip("/")
```

Línea 87:
```python
return f"{user_id}/Graficos"
```

**Estas subcarpetas NO deben existir.**

---

## 🔧 CORRECCIONES A APLICAR

### Corrección 1: Eliminar subcarpetas Informes/ y Graficos/

**Archivo:** `config.py`

**Cambio 1 - portfolio_json_path():**
```python
# ANTES
return f"{user_id}/Informes/{cls.SUPABASE_PORTFOLIO_FILENAME}".strip("/")

# DESPUÉS
return f"{user_id}/{cls.SUPABASE_PORTFOLIO_FILENAME}".strip("/")
```

**Cambio 2 - charts_prefix():**
```python
# ANTES
return f"{user_id}/Graficos"

# DESPUÉS
return f"{user_id}"
```

**Cambio 3 - build_chart_path():**
```python
# ANTES
if prefix:
    return f"{prefix}/{relative_clean}".strip("/")

# DESPUÉS
# Si user_id está en prefix, NO agregar subdirectorios
if prefix:
    # Extraer solo el nombre del archivo sin subdirectorios
    filename = Path(relative_clean).name
    return f"{prefix}/{filename}".strip("/")
```

---

### Corrección 2: Verificar allocation_chart usa datos dinámicos

**Archivo:** `portfolio_manager.py`

**Verificar línea 114:**
```python
# Asegurar que usa assets_to_process (dinámico) NO PORTFOLIO_CONFIG
allocation = self.calculator.calculate_asset_allocation(
    assets_to_process  # <-- Debe ser esta variable
)
```

**Verificar línea 270:**
```python
# Debe usar la misma fuente
allocation = self.calculator.calculate_asset_allocation(assets_data)
```

**Ambas deben referenciar los datos dinámicos del usuario, NO PORTFOLIO_CONFIG.**

---

## 📋 CHECKLIST DE VALIDACIÓN

Después de aplicar las correcciones:

- [ ] `config.py` modificado - Eliminar `/Informes` y `/Graficos`
- [ ] `portfolio_manager.py` verificado - `allocation` usa datos dinámicos
- [ ] Ejecutar `python generate_report.py --verbose`
- [ ] Verificar logs NO muestran "PORTFOLIO_CONFIG"
- [ ] Verificar Storage tiene estructura plana:
  ```
  portfolio-files/
  └── {user_id}/
      ├── portfolio_data.json
      ├── portfolio_chart.html
      └── allocation_chart.html
  ```
- [ ] Abrir `allocation_chart.html` y verificar que muestra assets del usuario, NO hardcodeados

---

## 🚀 PRÓXIMOS PASOS

1. **Aplicar correcciones en config.py**
2. **Verificar portfolio_manager.py**
3. **Eliminar carpetas antiguas en Storage** (Informes/ y Graficos/)
4. **Ejecutar test completo**
5. **Validar estructura en Supabase Dashboard**

---

**IMPORTANTE:** El bucle del worker es correcto y debe mantenerse. Solo corregir los otros 2 problemas.

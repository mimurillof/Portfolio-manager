# 🔧 Corrección Completa: Generación PNG en Heroku

## ✅ Cambios Aplicados

### 1. **chart_generator.py** - Método `_export_png_to_bytes()` reemplazado
- ❌ **ANTES**: Usaba `write_image()` con buffer `io.BytesIO()` (fallaba en Heroku)
- ✅ **AHORA**: Usa `fig.to_image()` directamente (método probado que funciona)

**Código anterior (NO funcionaba):**
```python
buffer = io.BytesIO()
fig.write_image(buffer, format="png", width=width, height=height)
buffer.seek(0)
img_bytes = buffer.read()
```

**Código nuevo (FUNCIONA):**
```python
img_bytes = fig.to_image(format="png", width=width, height=height)
```

### 2. **requirements.txt** - Versión fija de kaleido
```
kaleido==0.2.1  # Versión específica compatible con Heroku
```

### 3. **runtime.txt** - Versión de Python especificada
```
python-3.11.9
```

### 4. **Aptfile** - Dependencias del sistema Linux
Archivo nuevo con 20 librerías necesarias para renderizado gráfico.

### 5. **test_kaleido.py** - Script de prueba
Script automatizado para verificar que kaleido funcione correctamente.

## 🚀 Pasos para Desplegar

### 1. Agregar buildpack APT (CRÍTICO)
```bash
heroku buildpacks:add --index 1 heroku-community/apt -a TU_APP_NAME
```

### 2. Verificar buildpacks
```bash
heroku buildpacks -a TU_APP_NAME
```

Debe mostrar:
```
1. heroku-community/apt
2. heroku/python
```

### 3. Commit y push
```bash
git add .
git commit -m "Fix: Corregir generación PNG en Heroku con kaleido"
git push heroku main
```

### 4. Ejecutar prueba
```bash
heroku run python test_kaleido.py -a TU_APP_NAME
```

### 5. Verificar logs del worker
```bash
heroku logs --tail -a TU_APP_NAME | grep PNG
```

## 🎯 Resultado Esperado

Deberías ver en los logs:
```
✅ PNG generado correctamente (XXXXX bytes)
INFO:supabase_storage:Subiendo gráfico PNG a Supabase: ...
```

En lugar de:
```
WARNING:portfolio_manager:No PNG bytes generated for ...
```

## 🔍 Si aún no funciona

### Verificar stack de Heroku
```bash
heroku stack -a TU_APP_NAME
```

Si muestra `heroku-20`, actualizar a `heroku-22`:
```bash
heroku stack:set heroku-22 -a TU_APP_NAME
git commit --allow-empty -m "Trigger rebuild"
git push heroku main
```

### Verificar instalación de kaleido
```bash
heroku run "pip show kaleido" -a TU_APP_NAME
```

### Verificar dependencias del sistema
```bash
heroku run "dpkg -l | grep libglib" -a TU_APP_NAME
```

## 📚 Diferencias clave con el código funcional

El código de referencia que proporcionaste usa:
- `fig.write_image(filepath, ...)` para guardar a disco
- `fig.to_image(format="png", ...)` para obtener bytes

El problema en tu código era usar `write_image()` con un buffer en memoria, lo cual no funciona bien en Heroku. La solución es usar `to_image()` directamente.

---

**Fecha:** 22 de octubre de 2025  
**Status:** ✅ CORRECCIÓN COMPLETA APLICADA

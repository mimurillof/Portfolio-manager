# 🔧 Solución: Generación de PNG en Heroku

## Problema identificado

Las imágenes PNG de los gráficos no se estaban generando en Heroku debido a la falta de dependencias del sistema necesarias para que `kaleido` funcione correctamente.

## Cambios realizados

### 1. **Método de exportación PNG corregido** (`chart_generator.py`)

Se reemplazó completamente el método `_export_png_to_bytes()` con la implementación **probada y funcional**:
- ✅ Usa `fig.to_image()` directamente (método que funciona en Heroku)
- ✅ Sin buffer intermedio (simplificado)
- ✅ Validación de bytes generados
- ✅ Logs descriptivos con emojis para facilitar debugging

### 2. **Versión específica de kaleido**

Se fijó la versión exacta en `requirements.txt`:
```
kaleido==0.2.1
```
Esto evita incompatibilidades con versiones más recientes.

### 3. **Archivos de configuración para Heroku**

#### `runtime.txt` (NUEVO)
```
python-3.11.9
```
Especifica la versión de Python compatible con kaleido.

#### `Aptfile` (NUEVO)
Lista las dependencias del sistema Linux necesarias para renderizado gráfico:
- `libglib2.0-0`, `libnss3`, `libnspr4`
- `libatk1.0-0`, `libatk-bridge2.0-0`
- `libcups2`, `libdrm2`, `libdbus-1-3`
- `libxcb1`, `libxkbcommon0`, `libatspi2.0-0`
- `libx11-6`, `libxcomposite1`, `libxdamage1`
- `libxext6`, `libxfixes3`, `libxrandr2`
- `libgbm1`, `libpango-1.0-0`, `libcairo2`
- `libasound2`

## Configuración en Heroku

### Paso 1: Agregar el buildpack APT

Ejecuta este comando en tu terminal local (con Heroku CLI instalado):

```bash
heroku buildpacks:add --index 1 heroku-community/apt -a TU_APP_NAME
```

Reemplaza `TU_APP_NAME` con el nombre de tu aplicación en Heroku.

### Paso 2: Verificar los buildpacks

```bash
heroku buildpacks -a TU_APP_NAME
```

Deberías ver algo como:
```
1. heroku-community/apt
2. heroku/python
```

El orden es importante: APT debe ir **antes** de Python.

### Paso 3: Desplegar los cambios

```bash
git add .
git commit -m "Fix: Agregar soporte para exportación PNG en Heroku"
git push heroku main
```

### Paso 4: Verificar logs

```bash
heroku logs --tail -a TU_APP_NAME
```

Busca estos mensajes de éxito:
- ✅ `PNG generado en memoria correctamente (X bytes)`
- ✅ `Gráfico guardado como PNG: ...`

## Verificación de la solución

### Prueba automatizada (RECOMENDADO)

Ejecuta el script de prueba para verificar que kaleido funcione:

```bash
heroku run python test_kaleido.py -a TU_APP_NAME
```

Este script ejecuta 4 pruebas:
1. ✅ Importación de kaleido
2. ✅ Importación de plotly
3. ✅ Generación de PNG en memoria
4. ✅ Escritura de PNG a archivo

### Pruebas manuales

1. **Verificar que kaleido esté instalado:**
   ```bash
   heroku run python -c "import kaleido; print(kaleido.__version__)" -a TU_APP_NAME
   ```

2. **Verificar las dependencias del sistema:**
   ```bash
   heroku run "dpkg -l | grep libglib" -a TU_APP_NAME
   ```

3. **Probar la generación de PNG manualmente:**
   ```bash
   heroku run python -c "import plotly.graph_objects as go; fig = go.Figure(); fig.write_image('test.png')" -a TU_APP_NAME
   ```

## Notas importantes

- ⚠️ El buildpack APT solo funciona en el stack `heroku-22` o superior
- ⚠️ Si usas `heroku-20`, necesitas actualizar: `heroku stack:set heroku-22 -a TU_APP_NAME`
- 💡 Los archivos PNG se generan **en memoria** (como bytes) y luego se suben a Supabase
- 💡 Si la exportación PNG falla, el sistema automáticamente genera HTML como fallback

## Documentación de referencia

- [Heroku APT Buildpack](https://github.com/heroku/heroku-buildpack-apt)
- [Kaleido Documentation](https://github.com/plotly/Kaleido)
- [Plotly Static Image Export](https://plotly.com/python/static-image-export/)

---

**Fecha:** 22 de octubre de 2025  
**Autor:** Portfolio Manager Team  
**Versión:** 2.1.0

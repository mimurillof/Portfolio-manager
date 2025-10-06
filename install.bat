@echo off
echo ========================================
echo INSTALACION DE PORTFOLIO MANAGER
echo ========================================
echo.

echo Instalando dependencias Python...
pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo INSTALACION COMPLETADA
    echo ========================================
    echo.
    echo Ejecutando pruebas...
    python test_setup.py
) else (
    echo.
    echo ERROR: No se pudieron instalar las dependencias
    echo Por favor, verifica tu conexion a internet y Python
)

echo.
pause

@echo off
echo ====================================
echo   Portfolio Manager Service
echo   Puerto: 9000
echo ====================================
echo.

cd /d "%~dp0"

python -m uvicorn api_service:app --host 0.0.0.0 --port 9000 --reload

pause


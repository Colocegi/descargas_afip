@echo off
cd /d "%~dp0"
echo Descargando comprobantes del mes pasado...
python descargar_comprobantes.py
pause

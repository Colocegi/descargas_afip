@echo off
setlocal EnableDelayedExpansion

:: Intentar detectar ruta de OpenSSL
set OPENSSL_PATH=C:\Program Files\OpenSSL-Win64\bin\openssl.exe
if not exist "!OPENSSL_PATH!" (
    set OPENSSL_PATH=C:\OpenSSL-Win64\bin\openssl.exe
)
if not exist "!OPENSSL_PATH!" (
    echo ❌ No se pudo encontrar openssl.exe. Asegurate de que OpenSSL esté instalado.
    pause
    exit /b 1
)

echo ✅ Usando OpenSSL desde: !OPENSSL_PATH!

:: Crear carpeta de salida
mkdir certificados 2>nul

:: Leer CUITs del archivo
for /f "delims=" %%i in (cuit_list.txt) do (
  if not "%%i"=="" (
    echo 🔐 Generando certificado para CUIT: %%i
    "!OPENSSL_PATH!" genrsa -out certificados\%%i.key 2048
    "!OPENSSL_PATH!" req -new -key certificados\%%i.key -subj "/CN=%%i" -out certificados\%%i.csr
  )
)

echo.
echo ✅ Archivos .key y .csr generados en la carpeta certificados/
pause

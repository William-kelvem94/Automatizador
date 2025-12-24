@echo off
chcp 65001 >nul
title 🚀 Automatizador de Login

cls
echo.
echo ============================================
echo         🚀 AUTOMATIZADOR DE LOGIN
echo ============================================
echo.
echo [INFO] Iniciando interface grafica...
echo [INFO] Aguarde, a janela vai abrir em alguns segundos...
echo.

REM Verificar se Python existe
if not exist "C:\Python311\python.exe" (
    echo [ERRO] Python nao encontrado em C:\Python311!
    echo.
    echo [INFO] Execute primeiro: install.bat
    echo.
    pause
    exit /b 1
)

REM Mudar para o diretório do projeto
cd /d "%~dp0"

REM Executar a interface gráfica diretamente
echo [OK] Abrindo interface grafica...
start "" "C:\Python311\python.exe" "../src/gui.py"

echo.
echo [SUCCESS] Interface grafica iniciada com sucesso!
echo.
echo [INFO] Uma janela separada deve ter aberto.
echo [INFO] Se nao abriu, execute manualmente:
echo        C:\Python311\python.exe gui.py
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause >nul

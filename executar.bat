@echo off
chcp 65001 >nul
title 🚀 Automatizador de Login - Interface Moderna

cls
echo.
echo ============================================
echo         🚀 AUTOMATIZADOR DE LOGIN
echo ============================================
echo [VERSION] Interface Moderna v3.0
echo.
echo [INFO] Iniciando interface grafica moderna...
echo [INFO] Aguarde, a janela vai abrir em alguns segundos...
echo.

REM Verificar se Python existe
if not exist "C:\Python311\python.exe" (
    echo [ERRO] Python nao encontrado em C:\Python311!
    echo.
    echo [INFO] Execute primeiro: scripts\install.bat
    echo.
    pause
    exit /b 1
)

REM Mudar para o diretório do projeto
cd /d "%~dp0"

REM Executar a nova interface gráfica moderna
echo [OK] Abrindo interface grafica moderna...
start "" "C:\Python311\python.exe" src/gui_moderna.py

echo.
echo [SUCCESS] Interface grafica moderna iniciada!
echo.
echo [INFO] Uma janela moderna deve ter aberto.
echo [INFO] Se nao abriu, execute manualmente:
echo        C:\Python311\python.exe src/gui_moderna.py
echo.
echo [FEATURES] Interface moderna com:
echo   • Design profissional e intuitivo
echo   • Logs detalhados em tempo real
echo   • Operações automatizadas
echo   • Agendamento inteligente
echo   • Validação avançada
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause >nul

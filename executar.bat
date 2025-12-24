@echo off
chcp 65001 >nul
title 🚀 Automatizador Web IA v7.0 - Versão Organizada

cls
echo.
echo ============================================
echo         🚀 AUTOMATIZADOR WEB IA v7.0
echo ============================================
echo         Versão Organizada - Clean Architecture
echo.
echo [INFO] Iniciando interface PySide6 moderna...
echo [INFO] Aguarde, a janela vai abrir em alguns segundos...
echo.

REM Detectar automaticamente onde o Python está instalado
echo [DETECT] Procurando Python no sistema...
where python >nul 2>&1
if %errorlevel% neq 0 (
    REM Tentar localizações comuns
    if exist "C:\Python311\python.exe" (
        set PYTHON_EXE=C:\Python311\python.exe
        echo [OK] Python encontrado em C:\Python311\
    ) else if exist "C:\Python312\python.exe" (
        set PYTHON_EXE=C:\Python312\python.exe
        echo [OK] Python encontrado em C:\Python312\
    ) else if exist "C:\Program Files\Python311\python.exe" (
        set PYTHON_EXE="C:\Program Files\Python311\python.exe"
        echo [OK] Python encontrado em Program Files
    ) else if exist "C:\Program Files\Python312\python.exe" (
        set PYTHON_EXE="C:\Program Files\Python312\python.exe"
        echo [OK] Python encontrado em Program Files
    ) else (
        echo [ERRO] Python nao encontrado no sistema!
        echo.
        echo [SOLUCAO] Instale Python 3.11+ de:
        echo          https://www.python.org/downloads/
        echo.
        echo [DICA] Marque "Add Python to PATH" durante a instalacao
        echo.
        pause
        exit /b 1
    )
) else (
    set PYTHON_EXE=python
    echo [OK] Python encontrado no PATH do sistema
)

REM Verificar se Python funciona
echo [TEST] Testando Python...
%PYTHON_EXE% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python encontrado mas nao funciona!
    echo.
    pause
    exit /b 1
)

echo [OK] Python testado com sucesso

REM Mudar para o diretório do projeto
cd /d "%~dp0"

REM Executar a interface revolucionária
echo [OK] Abrindo interface IA...
start "" %PYTHON_EXE% launcher.py

echo.
echo [SUCCESS] Interface IA iniciada com sucesso!
echo.
echo [INFO] Uma janela moderna deve ter aberto.
echo [INFO] Se nao abriu, execute manualmente:
echo        python launcher.py
echo.
echo ============================================
echo         🤖 FUNCIONALIDADES IA
echo ============================================
echo   • Interface moderna com tema escuro
echo   • Dashboard inteligente em tempo real
echo   • Detecção automática com IA
echo   • Agendamento preditivo inteligente
echo   • Modo híbrido com orientação
echo   • Backup automático inteligente
echo   • Notificações flutuantes animadas
echo   • Logs estruturados e coloridos
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause >nul
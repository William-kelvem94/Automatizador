@echo off
chcp 65001 >nul
title 🚀 Automatizador IA v5.0 - Inicializador

cd /d "%~dp0"

echo [BOOT] Iniciando sistema de auto-carregamento...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado no PATH!
    echo Por favor, instale o Python e marque a opção 'Add Python to PATH'.
    pause
    exit /b 1
)

python run.py
exit

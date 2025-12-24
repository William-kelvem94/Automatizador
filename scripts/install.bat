@echo off
echo ============================================
echo    AUTOMATIZADOR DE LOGIN - INSTALADOR
echo ============================================
echo.

echo [DETECT] Procurando Python no sistema...
where python >nul 2>&1
if %errorlevel% neq 0 (
    REM Tentar localizações comuns
    if exist "C:\Python311\python.exe" (
        set PYTHON_EXE=C:\Python311\python.exe
        set PIP_EXE=C:\Python311\Scripts\pip.exe
        echo [OK] Python encontrado em C:\Python311\
    ) else if exist "C:\Python312\python.exe" (
        set PYTHON_EXE=C:\Python312\python.exe
        set PIP_EXE=C:\Python312\Scripts\pip.exe
        echo [OK] Python encontrado em C:\Python312\
    ) else if exist "C:\Program Files\Python311\python.exe" (
        set PYTHON_EXE="C:\Program Files\Python311\python.exe"
        set PIP_EXE="C:\Program Files\Python311\Scripts\pip.exe"
        echo [OK] Python encontrado em Program Files
    ) else if exist "C:\Program Files\Python312\python.exe" (
        set PYTHON_EXE="C:\Program Files\Python312\python.exe"
        set PIP_EXE="C:\Program Files\Python312\Scripts\pip.exe"
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
    set PIP_EXE=pip
    echo [OK] Python encontrado no PATH do sistema
)

echo [TEST] Testando Python...
%PYTHON_EXE% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python encontrado mas nao funciona!
    echo.
    pause
    exit /b 1
)

echo [OK] Python testado com sucesso
echo [INSTALL] Instalando dependencias...
echo.

%PYTHON_EXE% -m pip install --upgrade pip
if errorlevel 1 (
    echo ERRO: Falha ao atualizar pip!
    pause
    exit /b 1
)

%PIP_EXE% install -r ../config/requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha na instalacao das dependencias!
    echo.
    echo [DICA] Tente executar como Administrador:
    echo        %PIP_EXE% install --user -r ../config/requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo.
echo ============================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo ============================================
echo.
echo Python localizado em: %PYTHON_EXE%
echo Projeto localizado em: %~dp0
echo.
echo Para usar o programa:
echo   1. Configure o arquivo config/config.ini
echo   2. Execute: executar.bat
echo.
echo ============================================
echo    FUNCIONALIDADES IA DISPONIVEIS
echo ============================================
echo.
echo   • Interface Moderna com Material Design
echo   • Dashboard Inteligente em Tempo Real
echo   • Detecção Automática com IA
echo   • Agendamento Preditivo Inteligente
echo   • Modo Híbrido com Orientação
echo   • Backup Automático Inteligente
echo   • Notificações Flutuantes Animadas
echo   • Logs Estruturados e Coloridos
echo.
pause

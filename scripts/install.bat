@echo off
echo ============================================
echo    AUTOMATIZADOR DE LOGIN - INSTALADOR
echo ============================================
echo.

echo Verificando se Python esta instalado em C:\Python311...
if not exist "C:\Python311\python.exe" (
    echo ERRO: Python nao encontrado em C:\Python311!
    echo.
    echo Execute o comando abaixo como Administrador:
    echo winget install --id Python.Python.3.11 --location "C:\Python311"
    echo.
    pause
    exit /b 1
)

echo Python encontrado em C:\Python311. Instalando dependencias...
echo.

C:\Python311\python.exe -m pip install --upgrade pip
if errorlevel 1 (
    echo ERRO: Falha ao atualizar pip!
    pause
    exit /b 1
)

C:\Python311\Scripts\pip.exe install -r ../config/requirements.txt
if errorlevel 1 (
    echo ERRO: Falha na instalacao das dependencias!
    pause
    exit /b 1
)

echo.
echo ============================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo ============================================
echo.
echo Python instalado em: C:\Python311
echo Projeto localizado em: %~dp0
echo.
echo Para usar o programa:
echo   1. Configure o arquivo config.ini com suas informacoes
echo   2. Execute: executar.bat
echo.
echo Comandos disponiveis:
echo   executar.bat          - Menu interativo
echo   executar.bat --map    - Mapear campos automaticamente
echo   executar.bat --test   - Testar login unico
echo   executar.bat --schedule - Iniciar agendador
echo.
pause

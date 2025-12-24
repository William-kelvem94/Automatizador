# Script PowerShell para executar o Automatizador de Login
# -*- coding: utf-8 -*-

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "        AUTOMATIZADOR DE LOGIN" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Python existe
$pythonPath = "C:\Python311\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "[ERRO] Python não encontrado em C:\Python311!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Execute primeiro: .\install.bat" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione Enter para continuar"
    exit 1
}

Write-Host "[INFO] Iniciando programa..." -ForegroundColor Green
Write-Host ""

# Mudar para o diretório do script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Executar o programa com todos os argumentos passados
& $pythonPath "../src/run.py" @Args

Write-Host ""
Write-Host "[INFO] Programa finalizado." -ForegroundColor Green
Write-Host ""
Read-Host "Pressione Enter para continuar"

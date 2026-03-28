# ASTRA - Setup Python
Write-Host "========================================"
Write-Host "  ASTRA - Instalador do Python" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""

$pythonVersion = "3.11.8"
$url = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$output = "$env:TEMP\python-installer.exe"

Write-Host "Baixando Python $pythonVersion..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $url -OutFile $output

Write-Host "Download completo!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================"
Write-Host "  IMPORTANTE!" -ForegroundColor Red
Write-Host "========================================"
Write-Host ""
Write-Host "Quando o instalador abrir:" -ForegroundColor White
Write-Host "1. Marcar: Add Python to PATH" -ForegroundColor Green
Write-Host "2. Clicar: Install Now" -ForegroundColor Green
Write-Host ""

Read-Host "Pressiona ENTER para continuar"

Write-Host "Abrindo instalador..." -ForegroundColor Yellow
Start-Process -FilePath $output -Wait

Write-Host ""
Write-Host "Instalacao completa!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:"
Write-Host "1. Fecha e reabre o terminal"
Write-Host "2. Executa: python --version"
Write-Host ""

Remove-Item $output -Force -ErrorAction SilentlyContinue

# ASTRA - Script de Instalação do Python
# =========================================
# Este script baixa e inicia o instalador do Python
# Requer execução manual do instalador

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🐍 ASTRA - Instalador do Python" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Versão do Python a instalar
$pythonVersion = "3.11.8"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerPath = "$env:TEMP\python-installer.exe"

Write-Host "📥 Baixando Python $pythonVersion..." -ForegroundColor Yellow
Write-Host "   URL: $pythonUrl" -ForegroundColor Gray
Write-Host ""

try {
    # Baixar instalador
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing -ErrorAction Stop
    
    Write-Host "✅ Download completo!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "⚠️  INSTRUÇÕES IMPORTANTES" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "O instalador será aberto. Certifica-te de:" -ForegroundColor White
    Write-Host ""
    Write-Host "  1. ☑️  Marcar 'Add Python to PATH'" -ForegroundColor Green
    Write-Host "      (MUITO IMPORTANTE!)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  2. ☑️  Escolher 'Install Now' ou 'Customize'" -ForegroundColor Green
    Write-Host ""
    Write-Host "  3. ✅  Aguardar conclusão da instalação" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $response = Read-Host "Pressiona ENTER para abrir o instalador"
    
    # Abrir instalador
    Write-Host "🚀 Abrindo instalador..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -Wait
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ Instalação Concluída!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor White
    Write-Host ""
    Write-Host "  1. Fechar e reabrir o terminal (importante!)" -ForegroundColor Yellow
    Write-Host "  2. Verificar instalação:" -ForegroundColor White
    Write-Host "     python --version" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Instalar dependências do ASTRA:" -ForegroundColor White
    Write-Host "     cd C:\Users\antonio\Desktop\jarvis_organized\jarvis_organized\astra" -ForegroundColor Gray
    Write-Host "     pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  4. Executar ASTRA:" -ForegroundColor White
    Write-Host "     python main.py" -ForegroundColor Gray
    Write-Host ""
    
    # Limpar instalador
    Write-Host "🗑️  Removendo instalador temporário..." -ForegroundColor Gray
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
    
    Write-Host ""
    Write-Host "✅ Pronto! Fecha este terminal e abre um novo." -ForegroundColor Green
    Write-Host ""
    
}
catch {
    Write-Host "❌ Erro ao baixar Python: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Alternativa:" -ForegroundColor Yellow
    Write-Host "   Visita: https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host "   Baixa e instala manualmente" -ForegroundColor White
    Write-Host ""
}

Write-Host "Pressiona qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

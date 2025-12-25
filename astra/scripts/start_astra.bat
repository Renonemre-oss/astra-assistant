@echo off
echo.
echo ================================
echo  🤖 ASTRA - Iniciando Modo Astra
echo ================================
echo.

cd /d "%~dp0"

REM Verificar se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado! Instale o Python primeiro.
    pause
    exit /b 1
)

REM Verificar arquivos principais
if not exist "Astra_voice_mode.py" (
    echo ❌ Arquivo Astra_voice_mode.py não encontrado!
    pause
    exit /b 1
)

echo ✅ Iniciando ASTRA em modo Astra...
echo 💡 Para sair, diga "Astra, sair" ou pressione Ctrl+C
echo.

python Astra_voice_mode.py

echo.
echo 👋 Astra encerrado!
pause

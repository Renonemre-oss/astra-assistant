@echo off
echo.
echo ================================
echo  🤖 ALEX - Iniciando Modo Jarvis
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
if not exist "jarvis_voice_mode.py" (
    echo ❌ Arquivo jarvis_voice_mode.py não encontrado!
    pause
    exit /b 1
)

echo ✅ Iniciando ALEX em modo Jarvis...
echo 💡 Para sair, diga "Jarvis, sair" ou pressione Ctrl+C
echo.

python jarvis_voice_mode.py

echo.
echo 👋 Jarvis encerrado!
pause
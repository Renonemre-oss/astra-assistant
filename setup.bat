@echo off
chcp 65001 >nul
title ASTRA - Instalação Automática

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║       ASTRA - Assistente com IA          ║
echo  ║       Instalação Automática (Windows)    ║
echo  ╚══════════════════════════════════════════╝
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERRO] Python nao encontrado.
    echo  Instala Python 3.9+ em: https://www.python.org/downloads/
    echo  Certifica-te de marcar "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% encontrado.

:: Criar ambiente virtual
echo.
echo  [1/4] A criar ambiente virtual...
if exist .venv (
    echo  [OK] Ambiente virtual ja existe, a usar existente.
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo  [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
    echo  [OK] Ambiente virtual criado.
)

:: Ativar ambiente virtual
call .venv\Scripts\activate.bat

:: Atualizar pip
echo.
echo  [2/4] A atualizar pip...
python -m pip install --upgrade pip --quiet

:: Instalar dependências
echo.
echo  [3/4] A instalar dependencias (pode demorar alguns minutos)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo  [AVISO] Algumas dependencias podem ter falhado.
    echo  Isto e normal - o ASTRA funcionara sem as funcionalidades opcionais.
)
echo  [OK] Dependencias instaladas.

:: Verificar Ollama
echo.
echo  [4/4] A verificar Ollama...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [AVISO] Ollama nao encontrado.
    echo  Instala em: https://ollama.ai
    echo  Depois executa: ollama pull llama3.2
) else (
    echo  [OK] Ollama encontrado. A descarregar modelo llama3.2...
    ollama pull llama3.2
)

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   Instalacao concluida!                  ║
echo  ║                                          ║
echo  ║   Para iniciar o ASTRA:                  ║
echo  ║     .venv\Scripts\activate               ║
echo  ║     python -m astra                      ║
echo  ╚══════════════════════════════════════════╝
echo.
pause

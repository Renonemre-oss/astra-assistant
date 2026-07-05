#!/usr/bin/env bash
# ASTRA - Instalação Automática (Linux / macOS)

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}[OK]${NC} $1"; }
warn() { echo -e "  ${YELLOW}[AVISO]${NC} $1"; }
err()  { echo -e "  ${RED}[ERRO]${NC} $1"; }

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║       ASTRA - Assistente com IA          ║"
echo "  ║   Instalação Automática (Linux / macOS)  ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# ── 0. Verificar Python ──────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PYBIN="python3"
elif command -v python &>/dev/null; then
    PYBIN="python"
else
    err "Python não encontrado."
    echo "     Instala Python 3.9+ em: https://www.python.org/downloads/"
    exit 1
fi

PYVER=$($PYBIN --version 2>&1 | awk '{print $2}')
ok "Python $PYVER encontrado."

# ── 1. Ambiente virtual ──────────────────────────────────────────
echo ""
echo "  [1/4] A criar ambiente virtual..."
if [ -d ".venv" ]; then
    ok "Ambiente virtual já existe."
else
    $PYBIN -m venv .venv
    ok "Ambiente virtual criado."
fi

# Ativar
# shellcheck disable=SC1091
source .venv/bin/activate

# ── 2. Atualizar pip ─────────────────────────────────────────────
echo ""
echo "  [2/4] A atualizar pip..."
pip install --upgrade pip --quiet
ok "pip atualizado."

# ── 3. Instalar dependências ─────────────────────────────────────
echo ""
echo "  [3/4] A instalar dependências (pode demorar alguns minutos)..."
if pip install -r requirements.txt; then
    ok "Dependências instaladas."
else
    warn "Algumas dependências opcionais falharam. O ASTRA funcionará sem elas."
fi

# ── 4. Verificar Ollama ──────────────────────────────────────────
echo ""
echo "  [4/4] A verificar Ollama..."
if command -v ollama &>/dev/null; then
    ok "Ollama encontrado. A descarregar modelo llama3.2..."
    ollama pull llama3.2
else
    warn "Ollama não encontrado."
    echo "     Instala em: https://ollama.ai"
    echo "     Depois executa: ollama pull llama3.2"
fi

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   Instalação concluída!                  ║"
echo "  ║                                          ║"
echo "  ║   Para iniciar o ASTRA:                  ║"
echo "  ║     source .venv/bin/activate            ║"
echo "  ║     python -m astra                      ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

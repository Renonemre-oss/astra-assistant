# 🐧 Guia de Instalação - Linux

Guia completo para instalar e configurar o Astra AI Assistant no Linux (Ubuntu, Linux Mint, Debian e derivados).

---

## 📋 Pré-requisitos

### Sistema Operacional
- Ubuntu 20.04+ / Linux Mint 20+ / Debian 11+
- Python 3.10 ou superior
- 4GB RAM (mínimo)
- 2GB espaço em disco

### Dependências do Sistema

```bash
# Atualizar repositórios
sudo apt update

# Python e ferramentas de desenvolvimento
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Áudio (escolha uma das opções ou instale todas)
sudo apt install -y alsa-utils          # Para aplay (ALSA)
sudo apt install -y pulseaudio-utils    # Para paplay (PulseAudio)
sudo apt install -y ffmpeg              # Para ffplay (recomendado)

# PyAudio (necessário para reconhecimento de voz)
sudo apt install -y portaudio19-dev python3-pyaudio

# Text-to-Speech (espeak)
sudo apt install -y espeak espeak-ng espeak-data

# Opcional: Vozes em português para espeak
sudo apt install -y espeak-ng-espeak mbrola mbrola-br1 mbrola-br3

# Tesseract OCR (opcional, para reconhecimento de texto em imagens)
sudo apt install -y tesseract-ocr tesseract-ocr-por

# Git (se ainda não tiver)
sudo apt install -y git
```

---

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
# Clonar projeto
git clone https://github.com/Renonemre-oss/astra-assistant.git
cd astra-assistant
```

### 2. Criar Ambiente Virtual

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate

# Atualizar pip
pip install --upgrade pip setuptools wheel
```

### 3. Instalar Dependências Python

```bash
# Instalar todas as dependências
pip install -r requirements.txt
```

### 4. Configurar Ollama (IA Local - Recomendado)

```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Baixar modelo de IA em português
ollama pull llama3.2

# Verificar se está rodando
ollama list
```

### 5. Configurar API Keys (Opcional)

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas chaves
nano .env
```

---

## ⚙️ Configuração

### Verificar Áudio

```bash
# Testar alto-falantes
speaker-test -t wav -c 2

# Testar TTS
espeak-ng -v pt-BR "Olá, teste de áudio"

# Verificar dispositivos de áudio
aplay -l    # ALSA
pactl list  # PulseAudio
```

### Configurar TTS

O Astra detecta automaticamente o sistema de áudio disponível:
1. **Piper TTS** (melhor qualidade) - se instalado
2. **espeak/espeak-ng** (padrão Linux) - fallback
3. **pygame/aplay/paplay/ffplay** para reprodução

---

## 🎯 Executar o Astra

### Aplicação Principal (GUI)

```bash
# Ativar ambiente virtual (se não estiver ativo)
source .venv/bin/activate

# Executar ASTRA
python astra/main.py
```

### Comandos Disponíveis

```bash
python astra/main.py          # Executar aplicação
python astra/main.py test     # Executar testes
python astra/main.py diag     # Diagnóstico do sistema
python astra/main.py clean    # Limpar arquivos temporários
```

---

## 🔧 Solução de Problemas

### PyAudio não instala

```bash
sudo apt install -y portaudio19-dev python3-dev
pip install pyaudio
```

### Sem som / TTS não funciona

```bash
which espeak-ng
espeak-ng -v pt-BR "teste"
sudo apt install --reinstall espeak-ng
pip install pygame
```

### Ollama não responde

```bash
systemctl status ollama
sudo systemctl start ollama
sudo systemctl enable ollama
```

---

## ✅ Checklist Pós-Instalação

- [ ] Python 3.10+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas sem erros
- [ ] Sistema de áudio funcionando
- [ ] Ollama instalado e rodando
- [ ] Aplicação inicia sem erros

---

**Dúvidas?** Consulte a documentação completa em `docs/` ou abra uma issue no GitHub.

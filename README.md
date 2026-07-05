<div align="center">

# 🌌 ASTRA
### Assistente Pessoal com Inteligência Afetiva

*Estados emocionais reais. Memória contínua. Voz natural.*

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6-green?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%7C%20dolphin--llama3-orange)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

</div>

---

## O que é o ASTRA?

O **ASTRA** é um assistente pessoal construído em Python, focado em **acompanhamento emocional autêntico**.

Ao contrário de assistentes genéricos, o ASTRA possui **estados afetivos internos** — confiança, proximidade, irritação, envolvimento — que evoluem gradualmente a cada interação e moldam diretamente como responde, fala e se expressa.

> *"Estados mudam devagar. ASTRA acumula, não explode. Função antes de emoção — sempre."*

---

## Funcionalidades

### 🧠 Motor Afetivo
Estados internos contínuos `[0.0 → 1.0]` que persistem entre sessões (SQLite):

| Estado | Tipo | Descrição |
|---|---|---|
| `trust` | Relacional | Confiança acumulada na relação |
| `closeness` | Relacional | Proximidade emocional |
| `respect` | Relacional | Respeito mútuo |
| `care` | Relacional | Cuidado demonstrado |
| `engagement` | Engajamento | Vontade de participar |
| `patience` | Engajamento | Paciência disponível |
| `irritation` | Tensão | Irritação acumulada |
| `withdrawal` | Tensão | Afastamento emocional |
| `disappointment` | Tensão | Desapontamento acumulado |

Os estados **decaem automaticamente** com o tempo: os negativos recuperam mais rápido, os positivos constroem-se devagar.

### 🎭 Modulador de Expressão
Traduz estados afetivos internos em expressão percetível:
- Comprimento de frase (curto quando irritado, elaborado quando envolvido)
- Pontuação e energia textual (`.` seco, `!` entusiasta, `...` hesitante)
- Frequência de emojis (zero quando desiludido, frequente quando próximo)
- Tom de voz TTS (velocidade, pausas, volume, variação de pitch)

### ⚖️ Motor de Decisão
O ASTRA não é obediente cego — tem limites, pode discordar e recusar: `COMPLY`, `COMPLY_RELUCTANT`, `CLARIFY`, `REDIRECT`, `REFUSE_SOFT`, `REFUSE_FIRM`, `WITHDRAW`, `CONFRONT`.

### 🗃️ Sistema de Memória
Memória multi-camada com *decay* diferenciado: episódica, semântica, procedimental, de trabalho e emocional. As memórias emocionais têm *decay* mais agressivo para evitar ressentimento acumulado.

### 🎙️ Voz
- Hotword detection com **Porcupine** / **Vosk** (`"Astra"`, `"Hey ASTRA"`)
- STT offline com **Vosk** (modelo `vosk-model-small-pt`)
- TTS com **Piper** (modelo `pt_PT-tugao-medium` incluído) e suporte experimental a clonagem de voz (XTTS)
- Parâmetros prosódicos ajustados em tempo real pelo estado afetivo

### 🖥️ Interface e outras capacidades
- Interface **PyQt6** (tema escuro), não-bloqueante com threading
- Pesquisa na internet via **DuckDuckGo**
- OCR com **Tesseract** + **OpenCV**
- Classificação de intenções com **scikit-learn**
- Sistema RAG opcional (`astra/ai/`)

---

## Estrutura do Projeto

```
Astra/
├── astra/                    ← Pacote principal
│   ├── main.py               ← Launcher (python -m astra)
│   ├── core/assistant.py     ← Interface gráfica + loop principal
│   ├── modules/
│   │   ├── affective_state_engine.py   ← Estados afetivos + decay + persistência
│   │   ├── decision_engine.py          ← Significado → conflito → decisão
│   │   ├── expression_modulator.py     ← Estados → expressão
│   │   ├── memory_system.py            ← Memória multi-camada
│   │   ├── personality_engine.py       ← Análise de humor + modos adaptativos
│   │   ├── audio/ · speech/ · ui/ · database/ · experimental/
│   │   └── external_apis/              ← Meteorologia, notícias, email…
│   ├── ai/                   ← RAG, embeddings, providers (Ollama/OpenAI)
│   ├── api_server/           ← API REST (FastAPI)
│   ├── config/
│   │   ├── constants.py      ← Fonte única: paths + feature flags
│   │   └── settings/         ← main_config.py, voice_config.json
│   ├── security/ · utils/
│   ├── data/                 ← Dados de runtime (não versionados)
│   └── tests/                ← Testes unitários e de integração
├── docs/                     ← Documentação e guias
├── scripts/                  ← Scripts utilitários
├── tests/                    ← Testes adicionais (RAG, manuais)
├── requirements.txt
├── setup.bat / setup.sh      ← Instalação automática
└── README.md
```

### Fluxo de uma interação

```
Utilizador fala
      ↓
[Hotword Detection]    ← Porcupine / Vosk
      ↓
[STT - Transcrição]    ← Vosk offline
      ↓
[Decision Engine]      ← Analisa significado + limites
      ↓
[Affective Engine]     ← Atualiza estados internos
      ↓
[LLM - Ollama]         ← Gera resposta com tom ajustado
      ↓
[Expression Modulator] ← Ajusta estilo textual e prosódico
      ↓
[TTS - Piper]          ← Síntese de voz com parâmetros afetivos
      ↓
ASTRA responde
```

---

## Instalação

### Pré-requisitos

- **Python 3.9+** → [python.org](https://www.python.org/downloads/)
- **Ollama** com o modelo `dolphin-llama3:8b` → [ollama.ai](https://ollama.ai)
- **Tesseract OCR** *(opcional, para OCR de imagens)*

### Opção A — Download direto

1. Clica em **Code → Download ZIP** ou usa o [link direto](https://github.com/Renonemre-oss/astra-assistant/archive/refs/heads/main.zip)
2. Extrai o ZIP para uma pasta à tua escolha
3. Executa o script de instalação:

```batch
:: Windows — duplo clique ou:
setup.bat
```

```bash
# Linux / macOS
chmod +x setup.sh && ./setup.sh
```

O script cria o ambiente virtual, instala as dependências e configura o Ollama.

### Opção B — Clonar com git

```bash
git clone https://github.com/Renonemre-oss/astra-assistant.git
cd astra-assistant
./setup.sh   # ou setup.bat no Windows
```

### Iniciar o ASTRA

```batch
:: Windows
.venv\Scripts\activate
python -m astra
```

```bash
# Linux / macOS
source .venv/bin/activate
python -m astra
```

Outros comandos: `python -m astra test | diag | profile | perf | help`

### (Opcional) Modelo Vosk em Português

Descarrega `vosk-model-small-pt-0.3` de [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) e coloca em `astra/models/vosk-model-small-pt-0.3`.

---

## Configuração

| Ficheiro | O que configura |
|---|---|
| `astra/config/constants.py` | Feature flags, paths, limites |
| `astra/config/settings/main_config.py` | Modelo Ollama, timeouts, TTS |
| `astra/config/settings/voice_config.json` | Hotword, Vosk, Porcupine, TTS |
| `.env` (copiar de `.env.example`) | Chaves de API, `DATABASE_URL` |

### Base de dados

Por padrão o ASTRA usa **SQLite local** — não precisas de configurar nada. Para usar **MySQL remoto** (ex.: [Railway](https://railway.app)), define no `.env`:

```bash
DATABASE_URL=mysql://user:password@host:porta/database
```

No Railway: cria um serviço **MySQL**, copia o valor de `MYSQL_URL` da aba *Variables* e cola no `.env`. Se a ligação remota falhar, o ASTRA recorre automaticamente ao SQLite local.

### Feature Flags (`constants.py`)

```python
# ── Core (ativo por padrão) ──────────────────────────────────
ENABLE_VOICE_LOOP        = True    # Loop de voz completo
ENABLE_BASIC_MEMORY      = True    # Memória episódica + semântica
ENABLE_BASIC_PERSONALITY = True    # Motor de personalidade
ENABLE_UI                = True    # Interface PyQt6
ENABLE_OLLAMA            = True    # Integração com Ollama

# ── Experimental (desativado por padrão) ─────────────────────
ENABLE_COMPANION_ENGINE    = False
ENABLE_BEHAVIORAL_ANALYZER = False
ENABLE_NEEDS_PREDICTOR     = False
ENABLE_ETHICAL_ANALYZER    = False
```

---

## Dependências Principais

| Pacote | Finalidade |
|---|---|
| `PyQt6` | Interface gráfica |
| `vosk` + `SpeechRecognition` | STT offline em Português |
| `pvporcupine` | Detecção de hotword |
| `scikit-learn` + `nltk` | NLP e classificação de intenções |
| `Pillow` + `pytesseract` + `opencv` | OCR e processamento de imagem |
| `duckduckgo-search` | Pesquisa na internet |

O motor TTS principal é o **Piper** (binário externo + modelo `.onnx` incluído em `astra/modules/speech/piper_models/`).

### Clonagem de voz (opcional)

A clonagem de voz (XTTS / Coqui `TTS`) **não está** no `requirements.txt` principal: o pacote fixa `numpy==1.22.0` e `tqdm==4.64.*` em Python ≤3.10, o que entra em conflito com as restantes dependências. Se quiseres esta funcionalidade, instala num ambiente virtual à parte:

```bash
python -m venv .venv-voice-cloning
.venv-voice-cloning\Scripts\activate   # ou: source .venv-voice-cloning/bin/activate
pip install -r requirements-voice-cloning.txt
```

Em Linux, o fallback de sistema (`pyttsx3`) usa o `espeak`, instalado via gestor de pacotes — não é um pacote Python:

```bash
sudo apt install espeak festival   # Debian/Ubuntu
```

---

## Documentação

- [docs/](docs/) — guias de configuração (hotword, voz, ElevenLabs, RAG, performance)
- [CHANGELOG.md](CHANGELOG.md) — histórico de versões
- [CONTRIBUTING.md](CONTRIBUTING.md) — como contribuir
- [SECURITY.md](SECURITY.md) — política de segurança

---

## Filosofia

- Os estados afetivos são **internos, graduais e persistentes** — não simulados nem forçados
- ASTRA **não obedece cegamente** — tem limites e pode recusar com dignidade
- O assistente **não cria dependência emocional** nem manipula o utilizador
- **Função antes de emoção** — cumpre sempre o pedido, mas com tom genuíno
- O código é **modular e explícito** — as *feature flags* são sempre respeitadas

---

## Licença

Distribuído sob a licença MIT. Consulta o ficheiro [LICENSE](LICENSE).

---

<div align="center">

Desenvolvido por **António Pereira** · [Renonemre-oss](https://github.com/Renonemre-oss)

</div>

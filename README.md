<div align="center">

# 🌌 ASTRA
### Assistente Pessoal com Inteligência Afetiva

*Estados emocionais reais. Memória contínua. Voz natural.*

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6-green?style=for-the-badge&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%7C%20llama3.2-orange?style=for-the-badge)](https://ollama.ai)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)](#compatibilidade)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](datalogs/LICENSE)
[![Author](https://img.shields.io/badge/Author-Antonio%20Pereira-blue?style=for-the-badge)](https://github.com/Renonemre-oss)

</div>

---

## O que é o ASTRA?

**ASTRA** é um assistente pessoal construído em Python, focado em **acompanhamento emocional autêntico**.

Ao contrário de assistentes genéricos, o ASTRA possui **estados afetivos internos reais** — confiança, proximidade, irritação, envolvimento — que evoluem gradualmente a cada interação e moldam diretamente como responde, fala e se expressa.

> *"Estados mudam devagar. ASTRA acumula, não explode. Função antes de emoção — sempre."*

**Não é produtividade. Não é negócio. É presença.**

---

## ✨ Funcionalidades

### 🧠 Motor Afetivo
Estados internos contínuos `[0.0 → 1.0]` que persistem entre sessões:

| Estado | Tipo | Descrição |
|---|---|---|
| `trust` | Relacional ✅ | Confiança acumulada na relação |
| `closeness` | Relacional ✅ | Proximidade emocional |
| `respect` | Relacional ✅ | Respeito mútuo |
| `care` | Relacional ✅ | Cuidado demonstrado |
| `engagement` | Engajamento ✅ | Vontade de participar |
| `patience` | Engajamento ✅ | Paciência disponível |
| `irritation` | Tensão ⚠️ | Irritação acumulada |
| `withdrawal` | Tensão ⚠️ | Afastamento emocional |
| `disappointment` | Tensão ⚠️ | Desapontamento acumulado |

Os estados **decaem automaticamente** com o tempo. Os negativos recuperam mais rápido; os positivos constroem-se devagar.

### 🎭 Modulador de Expressão
Traduز estados afetivos invisíveis em expressão percetível:
- Comprimento de frase (curto quando irritado, elaborado quando envolvido)
- Pontuação e energia textual (`.` seco, `!` entusiasta, `...` hesitante)
- Frequência de emojis (zero quando desiludido, frequente quando próximo)
- Tom de voz TTS (velocidade, pausas, volume, variação de pitch)

### ⚖️ Motor de Decisão
O ASTRA **não é obediente cego**. Tem limites, pode discordar e recusar:

| Decisão | Quando ocorre |
|---|---|
| `COMPLY` | Pedido normal |
| `COMPLY_RELUCTANT` | Cumpre, mas com reservas |
| `CLARIFY` | Pedido ambíguo |
| `REDIRECT` | Redireciona a conversa |
| `REFUSE_SOFT` | Limite suave atingido |
| `REFUSE_FIRM` | Limite firme — não negocia |
| `WITHDRAW` | Afastamento temporário |
| `CONFRONT` | Confronta comportamento |

### 🗃️ Sistema de Memória
Memória multi-camada com *decay* diferenciado:

- **Episódica** — Eventos específicos e experiências vividas
- **Semântica** — Conhecimento geral sobre o utilizador
- **Procedimental** — Como fazer coisas
- **De trabalho** — Contexto atual da conversa
- **Emocional** — Memórias emocionais *(sempre com contexto obrigatório)*

> Memórias emocionais têm *decay* 3× mais agressivo para evitar ressentimento acumulado.

### 🎙️ Loop de Voz
- Hotword detection com **Porcupine** e **Vosk** (`"Astra"`, `"Hey ASTRA"`)
- STT offline com **Vosk** (modelo `vosk-model-small-pt`)
- TTS com **Piper** — voz natural em Português de Portugal
- Parâmetros prosódicos ajustados em tempo real pelo estado afetivo

### 🖥️ Interface Gráfica
- Construída com **PyQt6** — tema escuro com acentos dourados
- Responsiva e não-bloqueante com threading
- Visualizador de hotword integrado

### 🔧 Outras Capacidades
- Pesquisa na internet via **DuckDuckGo**
- OCR com **Tesseract** + **OpenCV**
- Classificação de intenções com **scikit-learn**
- Base de dados **SQLite** para persistência
- **Skills** — framework extensível de competências

---

## 🏗️ Arquitectura

```
astra-assistant/
└── astra/
    ├── core/
    │   └── assistant.py              ← Ponto de entrada principal
    │
    ├── modules/
    │   ├── affective_state_engine.py ← 💫 Estados afetivos + decay + persistência
    │   ├── decision_engine.py        ← ⚖️  Significado → Conflito → Decisão
    │   ├── expression_modulator.py   ← 🎭 Estados → Expressão sentida
    │   ├── memory_system.py          ← 🗃️  Episódica, semântica, emocional
    │   ├── personality_engine.py     ← 🎨 Análise de humor + modos adaptativos
    │   ├── personal_profile.py       ← 👤 Perfil do utilizador
    │   ├── people_manager.py         ← 👥 Gestão de pessoas conhecidas
    │   ├── audio/                    ← 🔊 AudioManager
    │   ├── speech/                   ← 🎙️  Hotword + STT
    │   ├── ui/                       ← 🖥️  Componentes PyQt6
    │   └── database/                 ← 💾 DatabaseManager (SQLite)
    │
    ├── config/
    │   ├── constants.py              ← 🔑 Fonte única: paths + feature flags
    │   └── settings/
    │       ├── main_config.py        ← ⚙️  CONFIG dict + logging + diagnóstico
    │       └── voice_config.json     ← 🎤 Hotword, Vosk, TTS
    │
    ├── utils/                        ← Utilitários e processamento de texto
    ├── skills/                       ← Framework de skills extensível
    ├── data/                         ← Dados persistentes
    └── scripts/                      ← Scripts de instalação
```

### Fluxo de uma interação

```
Utilizador fala
      ↓
[Hotword Detection]  ←── Porcupine / Vosk
      ↓
[STT - Transcrição]  ←── Vosk offline
      ↓
[Decision Engine]    ←── Analisa significado + limites
      ↓
[Affective Engine]   ←── Atualiza estados internos
      ↓
[LLM - Ollama]       ←── Gera resposta com tom ajustado
      ↓
[Expression Modulator] ← Ajusta estilo textual e prosódico
      ↓
[TTS - Piper]        ←── Síntese de voz com parâmetros afetivos
      ↓
ASTRA responde
```

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.9+** → [python.org](https://www.python.org/downloads/)
- **Ollama** com o modelo `llama3.2` → [ollama.ai](https://ollama.ai)
- **Piper TTS** com modelo PT → [rhasspy/piper](https://github.com/rhasspy/piper)
- **Tesseract OCR** *(opcional, para processamento de imagens)*

---

### 📥 Opção A — Download direto (recomendado para quem não usa git)

**1. Descarregar o projeto**

Clica em **Code → Download ZIP** no topo desta página, ou usa o link direto:

> [**⬇️ Download ZIP**](https://github.com/Renonemre-oss/astra-assistant/archive/refs/heads/main.zip)

**2. Extrair a pasta**

Extrai o ZIP para uma pasta à tua escolha, por exemplo `C:\ASTRA` ou `~/astra`.

**3. Executar o script de instalação automática**

```batch
:: Windows — abre a pasta extraida e faz duplo-clique em:
setup.bat
```

```bash
# Linux / macOS — abre o terminal na pasta extraida e executa:
chmod +x setup.sh && ./setup.sh
```

O script faz tudo automaticamente: cria o ambiente virtual, instala as dependências e configura o Ollama.

**4. Iniciar o ASTRA**

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

---

### 🖥️ Opção B — Clonar com git (para desenvolvedores)

```bash
git clone https://github.com/Renonemre-oss/astra-assistant.git
cd astra-assistant
```

Depois segue os passos da Opção A a partir do passo 3, ou corre o script diretamente:

```batch
:: Windows
setup.bat
```

```bash
# Linux / macOS
chmod +x setup.sh && ./setup.sh
```

---

***(Opcional)* Configurar modelo Vosk em Português**

Descarrega `vosk-model-small-pt-0.3` de [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) e coloca em `astra/models/vosk-model-small-pt-0.3`.

---

## ⚙️ Configuração

### Ficheiros principais

| Ficheiro | O que configura |
|---|---|
| `astra/config/constants.py` | Feature flags, paths, limites |
| `astra/config/settings/main_config.py` | Modelo Ollama, timeouts, TTS |
| `astra/config/settings/voice_config.json` | Hotword, Vosk, Porcupine, TTS |

### Feature Flags (`constants.py`)

```python
# ── Core (SEMPRE ativo) ───────────────────────────────────────
ENABLE_VOICE_LOOP        = True    # Loop de voz completo
ENABLE_BASIC_MEMORY      = True    # Memória episódica + semântica
ENABLE_BASIC_PERSONALITY = True    # Motor de personalidade
ENABLE_SKILLS            = True    # Framework de skills
ENABLE_UI                = True    # Interface PyQt6
ENABLE_OLLAMA            = True    # Integração com Ollama

# ── Experimental (desativado por padrão) ─────────────────────
ENABLE_COMPANION_ENGINE  = False   # Tipos de companherismo complexos
ENABLE_BEHAVIORAL_ANALYZER = False # Análise comportamental profunda
ENABLE_NEEDS_PREDICTOR   = False   # Predição de necessidades
ENABLE_ETHICAL_ANALYZER  = False   # Análise ética profunda
```

### Hotword e Voz (`voice_config.json`)

```json
{
  "hotword": {
    "wake_words": ["Astra", "ASTRA", "hey ASTRA"],
    "sensitivity": 0.7,
    "engine": "auto"
  },
  "vosk": {
    "model_path": "models/vosk-model-small-pt-0.3",
    "sample_rate": 16000
  },
  "tts": {
    "engine": "auto",
    "voice_rate": 180,
    "voice_volume": 0.9
  }
}
```

---

## 🧪 Estado do Projecto

```
Total de ficheiros analisados : ~200
Linhas de código               : ~15 000
Módulos                        : 25
Testes de qualidade            : 6/6 ✅
Imports circulares             : 0
Paths hardcoded críticos       : 0
Compatibilidade                : Windows / Linux / macOS
```

---

## 🌍 Compatibilidade

| Sistema Operativo | Estado |
|---|---|
| 🐧 Linux | ✅ Suportado |
| 🪟 Windows | ✅ Suportado |
| 🍎 macOS | ✅ Suportado |

---

## 📦 Dependências Principais

| Pacote | Finalidade |
|---|---|
| `PyQt6` | Interface gráfica |
| `SpeechRecognition` | Reconhecimento de fala |
| `vosk` | STT offline em Português |
| `pvporcupine` | Detecção de hotword |
| `scikit-learn` + `nltk` | NLP e classificação de intenções |
| `Pillow` + `pytesseract` + `opencv` | OCR e processamento de imagem |
| `duckduckgo-search` | Pesquisa na internet |
| `colorlog` | Logging colorido |
| `pywin32` | Compatibilidade Windows *(condicional)* |

---

## 🧭 Filosofia

- Os estados afetivos são **internos, graduais e persistentes** — não simulados nem forçados
- ASTRA **não obedece cegamente** — tem limites e pode recusar com dignidade
- O assistente **não cria dependência emocional** nem manipula o utilizador
- **Função antes de emoção** — cumpre sempre o pedido, mas com tom genuíno
- O código é **modular e explícito** — sem magia escondida, sem comportamento inventado
- As *feature flags* são **sempre respeitadas**

---

## 📄 Licença

Distribuído sob a licença MIT. Consulta o ficheiro [`datalogs/LICENSE`](datalogs/LICENSE) para mais detalhes.

---


<div align="center">

*Co-Authored-By: Oz &lt;oz-agent@warp.dev&gt;*

</div>

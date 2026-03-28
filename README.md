# ASTRA — Assistente Pessoal com IA

> Assistente de voz e texto com estados afetivos coerentes, memória episódica e interface gráfica moderna.

---

## Sobre o Projeto

**ASTRA** é um assistente pessoal inteligente construído em Python, focado em **acompanhamento emocional autêntico** — não em produtividade ou negócios. Possui estados afetivos internos (confiança, proximidade, irritação, envolvimento) que evoluem gradualmente com base nas interações, moldando as respostas de forma genuína.

O projeto segue uma arquitectura modular, com código limpo, funções pequenas e testáveis, e respeito rigoroso por *feature flags* para controlar funcionalidades.

---

## Funcionalidades Principais

- **Loop de Voz** — Detecção de palavra de ativação (*hotword*), reconhecimento de fala (STT) e síntese de voz (TTS) com Piper
- **Interface Gráfica** — UI moderna construída com PyQt6, com tema escuro e animações
- **Motor Afetivo** — Estados internos coerentes que influenciam o tom e estilo das respostas
- **Sistema de Memória** — Memória episódica e semântica para recordar interações e factos sobre o utilizador
- **Perfil Pessoal & Pessoas** — Gestão de perfil do utilizador e pessoas conhecidas
- **Motor de Decisão** — Sistema interno de tomada de decisão contextual
- **Modulador de Expressão** — Ajusta o estilo de comunicação ao estado afetivo e contexto
- **Skills** — Framework de competências extensível
- **Pesquisa na Internet** — Integração com DuckDuckGo
- **OCR** — Processamento de imagens via Tesseract
- **Base de Dados** — Histórico e dados persistidos em SQLite

---

## Arquitectura

```
astra/
├── core/               # Assistente principal e lógica central
├── modules/
│   ├── affective_state_engine.py   # Motor de estados afetivos
│   ├── decision_engine.py          # Motor de decisão
│   ├── expression_modulator.py     # Modulador de expressão
│   ├── memory_system.py            # Sistema de memória
│   ├── personality_engine.py       # Motor de personalidade
│   ├── personal_profile.py         # Perfil do utilizador
│   ├── people_manager.py           # Gestão de pessoas
│   ├── audio/                      # Gestão de áudio
│   ├── speech/                     # Reconhecimento de fala e hotword
│   ├── ui/                         # Componentes de interface gráfica
│   └── database/                   # Gestão de base de dados
├── config/
│   ├── constants.py                # Constantes e feature flags
│   └── settings/                   # Configurações principais
├── utils/                          # Utilitários e processamento de texto
├── data/                           # Dados persistentes
└── scripts/                        # Scripts de instalação e configuração
```

---

## Pré-requisitos

- **Python** 3.9+
- **Ollama** — com o modelo `llama3.2` instalado ([ollama.ai](https://ollama.ai))
- **Piper TTS** — para síntese de voz em Português
- **Tesseract OCR** *(opcional)* — para processamento de imagens

---

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/Renonemre-oss/astra-assistant.git
cd astra-assistant
```

### 2. Criar e activar ambiente virtual

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```bash
pip install -r astra/requirements.txt
```

### 4. Instalar o Ollama e o modelo

```bash
# Instalar Ollama: https://ollama.ai
ollama pull llama3.2
```

### 5. Configurar o Piper TTS *(opcional)*

Descarrega o modelo de voz em Português em [rhasspy/piper](https://github.com/rhasspy/piper) e define o caminho em `astra/config/settings/voice_config.json`.

---

## Executar

```bash
# A partir da raiz do projecto
python -m astra
```

---

## Configuração

As principais opções encontram-se em:

| Ficheiro | Descrição |
|---|---|
| `astra/config/constants.py` | Feature flags (activar/desactivar módulos) |
| `astra/config/settings/main_config.py` | URLs, paths, modelo Ollama |
| `astra/config/settings/voice_config.json` | Configurações de voz e TTS |

### Feature Flags

Edita `astra/config/constants.py` para activar ou desactivar funcionalidades:

```python
ENABLE_VOICE_LOOP      = True   # Loop de voz principal
ENABLE_BASIC_MEMORY    = True   # Sistema de memória
ENABLE_BASIC_PERSONALITY = True # Motor de personalidade
ENABLE_SKILLS          = True   # Framework de skills
ENABLE_UI              = True   # Interface gráfica
ENABLE_OLLAMA          = True   # Integração com Ollama
```

---

## Compatibilidade

| Sistema Operativo | Estado |
|---|---|
| Linux | ✅ Suportado |
| Windows | ✅ Suportado |
| macOS | ✅ Suportado |

---

## Dependências Principais

| Pacote | Finalidade |
|---|---|
| `PyQt6` | Interface gráfica |
| `SpeechRecognition` | Reconhecimento de fala |
| `vosk` | Reconhecimento offline |
| `pvporcupine` | Detecção de hotword |
| `Pillow` + `pytesseract` | OCR |
| `duckduckgo-search` | Pesquisa na internet |
| `scikit-learn` | Classificação de intenções |
| `nltk` | Processamento de linguagem natural |

---

## Filosofia do Projecto

- Os estados afetivos são **internos e graduais** — não simulados nem forçados
- O assistente **não cria dependência emocional** nem manipula o utilizador
- O código é **modular e explícito** — sem magia escondida
- As *feature flags* são **sempre respeitadas**

---

## Licença

Distribuído sob a licença MIT. Consulta o ficheiro `datalogs/LICENSE` para mais detalhes.

---

*Co-Authored-By: Oz <oz-agent@warp.dev>*

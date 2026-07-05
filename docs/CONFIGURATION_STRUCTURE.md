# 🔧 ASTRA - Estrutura de Configuração

**Última atualização**: 2026-03-28  
**Versão**: 2.0.0-simplified

## 📋 Visão Geral

O ASTRA usa uma estrutura de configuração hierárquica com dois arquivos principais:

1. **`config/constants.py`** - Constantes do sistema (valores fixos)
2. **`config/settings/main_config.py`** - Configurações dinâmicas e funções

---

## 📁 Hierarquia de Arquivos de Configuração

```
astra/
├── config/
│   ├── __init__.py               # Exports principais
│   ├── constants.py              # ⭐ FONTE ÚNICA de constantes
│   └── settings/
│       ├── main_config.py        # ⭐ Configurações e funções
│       ├── speech_config.json    # Configurações de voz
│       └── voice_config.json     # Perfis de voz
```

---

## 🎯 Princípios de Design

### 1. **Fonte Única de Verdade**
- `constants.py` define todos os valores fixos
- `main_config.py` importa de `constants.py` quando necessário
- Outros módulos importam de `config/__init__.py`

### 2. **Separação de Responsabilidades**

#### `constants.py` contém:
- ✅ Paths do projeto (PROJECT_ROOT, DATA_DIR, LOGS_DIR)
- ✅ Feature flags (ENABLE_*)
- ✅ Valores numéricos fixos (timeouts, limites)
- ✅ Regex patterns
- ✅ Constantes de UI

#### `main_config.py` contém:
- ✅ CONFIG dict (configurações dinâmicas)
- ✅ UI_STYLES (estilos da interface)
- ✅ PERSONALITIES (modos de personalidade)
- ✅ Funções de configuração (configure_logging, check_dependencies)
- ✅ Funções de diagnóstico (validate_critical_dependencies, print_startup_diagnostics)

---

## 📦 Como Usar

### Importar Configurações

```python
# ✅ CORRETO - Importar de config/__init__.py
from astra.config import CONFIG, UI_STYLES, PERSONALITIES

# ✅ CORRETO - Importar constantes
from astra.config.constants import (
    PROJECT_ROOT,
    ENABLE_BASIC_MEMORY,
    MAX_TOKEN_LENGTH
)

# ✅ CORRETO - Importar funções específicas
from astra.config.settings.main_config import (
    configure_logging,
    check_dependencies,
    print_startup_diagnostics
)

# ❌ EVITAR - Import direto de arquivos internos
from astra.config.settings.main_config import PROJECT_ROOT  # Use constants.py!
```

---

## 🔑 Variáveis de Configuração Principais

### CONFIG Dictionary

```python
CONFIG = {
    # Modelo Ollama
    "ollama_model": "dolphin-llama3:8b",  # Modelo padrão
    "ollama_url": "http://localhost:11434/api/generate",
    
    # Conversação
    "conversation_history_size": 3,
    "max_retries": 3,
    "request_timeout": 120,
    
    # Arquivos de dados
    "lembretes_file": DATA_DIR / "lembretes.txt",
    "history_file": DATA_DIR / "conversation_history.json",
    "facts_file": DATA_DIR / "personal_facts.json",
    "log_file": LOGS_DIR / "ASTRA_assistant.log",
    
    # Modelo neural
    "model_file": NEURAL_DIR / "modelo.pkl",
    "intents_file": NEURAL_DIR / "dados" / "intents.json",
    
    # TTS/Audio
    "tts_model": "tts_models/pt/cv/vits",
    "temp_audio_file": PROJECT_ROOT / "audio" / "resposta_temp.wav",
}
```

### Feature Flags (constants.py)

```python
# Core Features (SEMPRE habilitados)
ENABLE_VOICE_LOOP = True             # Sistema de voz
ENABLE_SKILLS = True                 # Framework de skills
ENABLE_BASIC_MEMORY = True           # Memória episódica + semântica
ENABLE_BASIC_PERSONALITY = True      # Personalidade básica
ENABLE_UI = True                     # Interface PyQt6
ENABLE_OLLAMA = True                 # Integração Ollama

# Features Experimentais (DESABILITADAS por padrão)
ENABLE_COMPANION_ENGINE = False      # Companion types complexos
ENABLE_BEHAVIORAL_ANALYZER = False   # Análise comportamental profunda
ENABLE_NEEDS_PREDICTOR = False       # Predição de necessidades
ENABLE_OPINION_SYSTEM = False        # Sistema de opiniões complexo
ENABLE_ADVANCED_RAG = False          # RAG integration avançada
ENABLE_ETHICAL_ANALYZER = False      # Análise ética profunda
```

---

## 🛠️ Funções de Configuração

### Logging

```python
from astra.config.settings.main_config import configure_logging

# Configurar logging (chamado automaticamente em main.py)
logger = configure_logging()
```

### Diagnóstico de Sistema

```python
from astra.config.settings.main_config import (
    print_startup_diagnostics,
    validate_critical_dependencies,
    check_dependencies
)

# Verificar dependências críticas
ok, missing = validate_critical_dependencies()
if not ok:
    print(f"Faltando: {missing}")

# Diagnóstico completo com output formatado
can_start = print_startup_diagnostics()

# Verificar dependências específicas
deps = check_dependencies()
if deps['PyQt6']:
    print("PyQt6 disponível")
```

---

## 📝 Personalidades

```python
PERSONALITIES = {
    "neutra": {
        "greeting": "Olá! Como posso ajudar?",
        "style": "Responde de forma equilibrada e profissional."
    },
    "amigável": {
        "greeting": "Olá! Fico feliz em falar consigo! Como está?",
        "style": "Responde de forma calorosa, amigável e entusiástica."
    },
    "formal": {
        "greeting": "Bom dia. Em que posso ser útil?",
        "style": "Responde de forma formal e concisa."
    },
    "casual": {
        "greeting": "Ei! Tudo bem? O que precisa?",
        "style": "Responde de forma descontraída e informal."
    }
}
```

---

## 🎨 Estilos da UI

```python
UI_STYLES = {
    "main_style": """
        QWidget {
            background-color: transparent;
            color: #dddddd;
            font-family: 'Segoe UI';
        }
        /* ... mais estilos ... */
    """
}
```

---

## 🔄 Atualizar Configurações

### Adicionar Nova Constante

1. Editar `config/constants.py`:
```python
# Nova constante
NEW_FEATURE_TIMEOUT = 30  # segundos
```

2. Usar em módulos:
```python
from astra.config.constants import NEW_FEATURE_TIMEOUT

# Usar diretamente
timeout = NEW_FEATURE_TIMEOUT
```

### Adicionar Nova Configuração Dinâmica

1. Editar `config/settings/main_config.py`:
```python
CONFIG = {
    # ... existentes ...
    "new_setting": "valor_padrao",
}
```

2. Usar via CONFIG:
```python
from astra.config import CONFIG

value = CONFIG["new_setting"]
```

### Adicionar Nova Feature Flag

1. Editar `config/constants.py`:
```python
# Nova feature
ENABLE_NEW_FEATURE = False  # Desabilitada por padrão
```

2. Usar em módulos:
```python
from astra.config.constants import ENABLE_NEW_FEATURE

if ENABLE_NEW_FEATURE:
    # Ativar feature
    pass
```

3. Importar em `assistant.py` (se necessário):
```python
from ..config.constants import (
    # ... existentes ...
    ENABLE_NEW_FEATURE,
)
```

---

## ⚠️ Regras Importantes

### ✅ DO

- ✅ Usar `constants.py` para valores fixos
- ✅ Usar `CONFIG` para configurações que podem mudar
- ✅ Importar via `config/__init__.py` quando possível
- ✅ Documentar novas configurações
- ✅ Usar feature flags para código experimental
- ✅ Manter paths relativos a PROJECT_ROOT

### ❌ DON'T

- ❌ Duplicar constantes em múltiplos arquivos
- ❌ Hardcoded valores no código (use CONFIG ou constants)
- ❌ Modificar PROJECT_ROOT sem atualizar documentação
- ❌ Habilitar features experimentais sem testar
- ❌ Ignorar feature flags (sempre verificar antes de usar)

---

## 📊 Dependências e Estados

### Verificar Disponibilidade

```python
from astra.config import (
    DATABASE_AVAILABLE,
    TESSERACT_AVAILABLE,
    DEPENDENCIES
)

if DATABASE_AVAILABLE:
    # Usar database
    pass

if DEPENDENCIES['PyQt6']:
    # Usar PyQt6
    pass
```

---

## 🐛 Troubleshooting

### Problema: "Module not found" ao importar config

**Solução**: Verifique se está importando de `config/__init__.py`:
```python
# ✅ Correto
from astra.config import CONFIG

# ❌ Errado
from astra.config.settings.main_config import CONFIG
```

### Problema: PROJECT_ROOT aponta para lugar errado

**Solução**: `constants.py` define PROJECT_ROOT corretamente. Se precisar usar em outro arquivo:
```python
from astra.config.constants import PROJECT_ROOT
```

### Problema: Feature flag não funciona

**Solução**: 
1. Verificar se está definida em `constants.py`
2. Verificar se está importada em `assistant.py`
3. Verificar se há fallback no código

---

## 📚 Ver Também

- `docs/logging_system.md` - Sistema de logging
- `README.md` - Documentação geral
- `config/constants.py` - Todas as constantes
- `config/settings/main_config.py` - Funções de configuração

---

**Última revisão**: 2026-03-28  
**Autor**: António Pereira / Warp AI Assistant

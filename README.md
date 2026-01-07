# 🤖 Astra AI Assistant

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **Um assistente de IA modular, extensível e poderoso com suporte para múltiplos provedores de IA e sistema de skills plug-and-play.**

Astra é mais do que um simples assistente - é uma plataforma completa para construir experiências de IA personalizadas com privacidade, flexibilidade e poder.

---

## ✨ Por que Astra?

- **🔌 Modular**: Sistema de skills extensível - adicione novas capacidades sem modificar o core
- **🤖 Multi-IA**: Suporte para Ollama (local), OpenAI, e mais - com fallback automático
- **🔒 Privacidade**: Rode completamente local com Ollama - seus dados nunca saem da sua máquina
- **⚡ Inteligente**: Sistema de cache, memória contextual e RAG para respostas precisas
- **🎯 Simples**: Configuração via YAML, documentação clara e exemplos práticos
- **🚀 Pronto para Produção**: Logging robusto, tratamento de erros e métricas integradas

---

## 🚀 Quick Start

### 1. Instalação

**Linux/macOS:**
```bash
# Clone o repositório
git clone https://github.com/Renonemre-oss/astra-assistant.git
cd astra-assistant

# Instale dependências do sistema (Linux)
sudo apt install -y python3-venv python3-dev espeak-ng alsa-utils portaudio19-dev

# Crie ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale dependências Python
pip install -r requirements.txt
```

**Windows:**
```pwsh
# Clone o repositório
git clone https://github.com/Renonemre-oss/astra-assistant.git
cd astra-assistant

# Crie ambiente virtual
python -m venv .venv
.venv\\Scripts\\activate

# Instale dependências
pip install -r requirements.txt
```

> 🐧 **Linux:** Veja o guia completo em [`INSTALL_LINUX.md`](INSTALL_LINUX.md)

### 2. Configure a IA

**Opção A: Ollama (Local - Recomendado)**

*Linux/macOS:*
```bash
# Instale Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Baixe modelo
ollama pull llama3.2

# Configure em config/ai_config.yaml
default_provider: ollama
```

*Windows:*
```pwsh
# Baixe e instale de: https://ollama.ai
# Depois:
ollama pull llama3.2
```

**Opção B: OpenAI (Remoto)**
```bash
# Configure API key
export OPENAI_API_KEY=sua-chave-aqui  # Linux/macOS
# ou
$env:OPENAI_API_KEY="sua-chave-aqui"  # Windows

# Configure em config/ai_config.yaml
default_provider: openai
```

### 3. Execute

```bash
# Linux/macOS
python astra/main.py

# Windows
python astra\\main.py
```

Pronto! 🎉

---

## 📚 Arquitetura

```
Astra/
├── ai/                    # 🧠 Motor de IA Unificado
│   ├── ai_core_engine.py  # Gerenciador de provedores + fallback + cache
│   └── ai_providers/      # Ollama, OpenAI, etc.
├── skills/                # 🔌 Sistema de Skills
│   ├── base_skill.py      # Interface base para todas as skills
│   ├── builtin/           # Skills nativas (weather, news, memory, etc.)
│   └── custom/            # Suas skills personalizadas
├── config/                # ⚙️ Configurações
│   ├── ai_config.yaml     # Configuração de IA
│   └── skills_config.yaml # Configuração de skills
├── core/                  # 🎯 Core do assistente
├── modules/               # 📦 Módulos funcionais
└── docs/                  # 📖 Documentação completa
```

### Como funciona?

1. **Usuário faz uma pergunta** → `"Qual o clima em Lisboa?"`
2. **Skills analisam** → Weather skill detecta e processa
3. **AI Engine gera resposta** → Usa Ollama/OpenAI
4. **Resposta formatada** → Retorna ao usuário

---

## 🎯 Funcionalidades

### AI Engine

- ✅ **Múltiplos provedores**: Ollama, OpenAI (mais em breve)
- ✅ **Fallback automático**: Se um provider falha, tenta o próximo
- ✅ **Cache inteligente**: Evita requisições duplicadas
- ✅ **Streaming**: Respostas em tempo real
- ✅ **Configuração simples**: Tudo via YAML

### Sistema de Skills

- ✅ **Plug-and-play**: Adicione skills sem modificar o core
- ✅ **Auto-descoberta**: Skills são carregadas automaticamente
- ✅ **Priorização**: Controle ordem de execução
- ✅ **Validação**: Dependências e API keys verificadas automaticamente

### Skills Disponíveis

| Skill | Status | Descrição |
|-------|--------|-----------|
| Weather | ✅ Ativa | Previsão do tempo para qualquer cidade |
| News | 🚧 Em breve | Últimas notícias personalizadas |
| Memory | 🚧 Em breve | Sistema de memória inteligente |
| Calculator | 🚧 Em breve | Cálculos matemáticos complexos |
| Timer | 🚧 Em breve | Temporizadores e alarmes |

---

## 💡 Exemplos de Uso

### Exemplo Básico

```python
from Astra.ai import AIEngine
import yaml

# Carregar configuração
with open('config/ai_config.yaml') as f:
    config = yaml.safe_load(f)

# Inicializar AI Engine
engine = AIEngine(config)

# Fazer pergunta
response = engine.generate("Olá, como está o tempo hoje?")
print(response.content)
```

### Criar uma Skill Customizada

```python
from Astra.skills import BaseSkill, SkillMetadata, SkillResponse

class MinhaSkill(BaseSkill):
    def get_metadata(self):
        return SkillMetadata(
            name="Minha Skill",
            version="1.0.0",
            description="Uma skill incrível",
            keywords=["exemplo", "teste"]
        )
    
    def initialize(self):
        # Inicializar recursos
        return True
    
    def can_handle(self, query, context):
        # Verificar se pode processar a query
        return "exemplo" in query.lower()
    
    def execute(self, query, context):
        # Processar e retornar resposta
        return SkillResponse.success_response(
            "Esta é minha skill customizada!"
        )
```

Adicione em `config/skills_config.yaml`:
```yaml
custom_skills:
  minha_skill:
    enabled: true
    module: "skills.custom.minha_skill"
    class: "MinhaSkill"
```

---

## 📖 Documentação

- **[Getting Started](docs/guides/01_getting_started.md)** - Instalação e configuração completa
- **[AI Providers](docs/guides/04_ai_providers.md)** - Como configurar diferentes IAs
- **[Creating Skills](docs/guides/03_creating_skills.md)** - Tutorial completo de skills
- **[API Reference](docs/api/)** - Documentação completa da API
- **[Examples](examples/)** - Exemplos práticos

---

## 🛠️ Configuração

### AI Engine (`config/ai_config.yaml`)

```yaml
default_provider: ollama

providers:
  ollama:
    enabled: true
    model: llama3.2
    url: http://localhost:11434
  
  openai:
    enabled: false
    model: gpt-3.5-turbo
    api_key: ${OPENAI_API_KEY}

fallback_chain:
  - ollama
  # - openai  # Descomente para fallback

cache_enabled: true
cache_ttl: 3600
```

### Skills (`config/skills_config.yaml`)

```yaml
builtin_skills:
  weather:
    enabled: true
    config:
      openweather_api_key: ${OPENWEATHER_API_KEY}
      default_city: "São Paulo"

custom_skills:
  # Suas skills aqui
```

---

## 🤝 Contribuindo

Contribuições são muito bem-vindas! 

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaSkill`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova skill'`)
4. Push para a branch (`git push origin feature/NovaSkill`)
5. Abra um Pull Request

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

---

## 🗺️ Roadmap

### Fase 1: Fundação ✅ (Atual)
- [x] AI Engine unificado
- [x] Sistema de Skills modular
- [x] Weather Skill
- [x] Documentação básica

### Fase 2: Expansão 🚧
- [ ] News Skill
- [ ] Memory Skill  
- [ ] CLI melhorado
- [ ] Mais provedores de IA (Anthropic, Google)
- [ ] Testes automatizados

### Fase 3: Polimento 📋
- [ ] Interface Web
- [ ] Marketplace de Skills
- [ ] CI/CD completo
- [ ] Tutoriais em vídeo

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

**António Pereira** - [Renonemre-oss](https://github.com/Renonemre-oss)

---

## 🙏 Agradecimentos

- Comunidade Open Source
- [Ollama](https://ollama.ai) - IA local incrível
- [OpenAI](https://openai.com) - APIs poderosas
- Todos os contribuidores

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela! ⭐**

**📧 Dúvidas? Abra uma [issue](https://github.com/Renonemre-oss/astra-assistant/issues)**

**🚀 Happy coding!**

</div>




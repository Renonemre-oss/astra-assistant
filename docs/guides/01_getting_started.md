# 🚀 Getting Started - Jarvis AI Assistant

Bem-vindo ao Jarvis! Este guia vai te ajudar a configurar e executar o Jarvis em poucos minutos.

## 📋 Pré-requisitos

- **Python 3.8+** instalado
- **Git** para clonar o repositório
- **10 GB de espaço** em disco (para modelos de IA)
- **4 GB RAM** mínimo (8 GB recomendado)

## 🔧 Instalação Passo a Passo

### 1. Clone o Repositório

```bash
git clone https://github.com/Renonemre-oss/jarvis-ai-assistant.git
cd jarvis-ai-assistant
```

### 2. Crie um Ambiente Virtual

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale as Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure a IA

Você tem duas opções principais:

#### Opção A: Ollama (Local - Recomendado)

**Vantagens:**
- ✅ Privacidade total - tudo roda localmente
- ✅ Sem custos de API
- ✅ Funciona offline
- ✅ Rápido após download inicial

**Instalação:**

1. Instale o Ollama:
   - **Linux/Mac:** 
     ```bash
     curl -fsSL https://ollama.ai/install.sh | sh
     ```
   - **Windows:** Baixe de [ollama.ai](https://ollama.ai)

2. Baixe um modelo:
   ```bash
   ollama pull llama3.2
   # ou
   ollama pull mistral
   ```

3. Verifique se está funcionando:
   ```bash
   ollama list
   ```

4. Configure `jarvis/config/ai_config.yaml`:
   ```yaml
   default_provider: ollama
   
   providers:
     ollama:
       enabled: true
       model: llama3.2
       url: http://localhost:11434
   ```

#### Opção B: OpenAI (Remoto)

**Vantagens:**
- ✅ Modelos mais avançados (GPT-4)
- ✅ Sem necessidade de hardware potente
- ✅ Setup instantâneo

**Desvantagens:**
- ❌ Requer API key
- ❌ Tem custo por uso
- ❌ Requer internet

**Instalação:**

1. Crie conta em [platform.openai.com](https://platform.openai.com)

2. Obtenha API key

3. Configure variável de ambiente:
   ```bash
   # Linux/Mac
   export OPENAI_API_KEY=sk-...sua-chave...
   
   # Windows PowerShell
   $env:OPENAI_API_KEY="sk-...sua-chave..."
   ```

4. Configure `jarvis/config/ai_config.yaml`:
   ```yaml
   default_provider: openai
   
   providers:
     openai:
       enabled: true
       model: gpt-3.5-turbo
       api_key: ${OPENAI_API_KEY}
   ```

### 5. Configure as Skills (Opcional)

Edite `jarvis/config/skills_config.yaml`:

```yaml
builtin_skills:
  weather:
    enabled: true
    config:
      openweather_api_key: ""  # Deixe vazio para modo demo
      default_city: "Lisboa"   # Sua cidade
```

### 6. Execute o Jarvis!

```bash
cd jarvis
python main.py
```

Você deverá ver algo como:
```
🤖 JARVIS - Assistente Pessoal Inteligente
📁 Nova estrutura organizada carregada!
--------------------------------------------------
AI Engine inicializado. Provedor padrão: ollama
Skill ativada: Weather
Sistema iniciado com sucesso!
```

## 🎯 Primeiros Comandos

Experimente perguntar:

- "Olá, como você está?"
- "Qual o clima hoje?"
- "Qual o clima em Lisboa?"
- "Me conte uma piada"

## ⚙️ Configuração Adicional

### Ajustar Temperatura da IA

Em `config/ai_config.yaml`:

```yaml
defaults:
  temperature: 0.7  # 0.0 = mais preciso, 1.0 = mais criativo
```

### Ativar Mais Skills

Em `config/skills_config.yaml`:

```yaml
builtin_skills:
  weather:
    enabled: true
  news:
    enabled: true  # Ativar skill de notícias
```

### Configurar Cache

Em `config/ai_config.yaml`:

```yaml
cache_enabled: true
cache_ttl: 3600  # 1 hora em segundos
```

## 🐛 Troubleshooting

### Erro: "Ollama não está acessível"

**Solução:**
```bash
# Verificar se Ollama está rodando
ollama serve

# Em outro terminal
ollama list
```

### Erro: "Modelo llama3.2 não encontrado"

**Solução:**
```bash
ollama pull llama3.2
```

### Erro: "ModuleNotFoundError"

**Solução:**
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Erro: "API key não configurada"

**Solução:**
```bash
# Verificar variável de ambiente
echo $OPENAI_API_KEY  # Linux/Mac
echo $env:OPENAI_API_KEY  # Windows

# Configurar novamente se necessário
export OPENAI_API_KEY=sua-chave
```

## 📚 Próximos Passos

Agora que o Jarvis está funcionando:

1. **[Configure Provedores de IA](04_ai_providers.md)** - Aprenda mais sobre Ollama, OpenAI e outros
2. **[Crie sua Primeira Skill](03_creating_skills.md)** - Adicione novas capacidades
3. **[Explore Exemplos](../../examples/)** - Veja código prático
4. **[Leia a API](../api/)** - Documentação completa

## 🆘 Precisa de Ajuda?

- **Documentação:** [docs/](../)
- **Issues:** [GitHub Issues](https://github.com/Renonemre-oss/jarvis-ai-assistant/issues)
- **Exemplos:** [examples/](../../examples/)

---

**✨ Parabéns! Você configurou o Jarvis com sucesso! ✨**

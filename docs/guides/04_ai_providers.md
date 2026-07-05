# 🤖 AI Providers - Astra AI Assistant

Este guia explica como configurar e usar diferentes provedores de IA com o Astra.

## 📋 Visão Geral

O Astra suporta múltiplos provedores de IA através do **AI Engine**, permitindo:

- ✅ Usar IA local (Ollama) ou remota (OpenAI)
- ✅ Fallback automático entre provedores
- ✅ Trocar de provedor sem modificar código
- ✅ Usar múltiplos provedores simultaneamente

## 🎯 Provedores Disponíveis

| Provedor | Tipo | Custo | Privacidade | Qualidade |
|----------|------|-------|-------------|-----------|
| **Ollama** | Local | Grátis | 🟢 Total | 🟡 Boa |
| **OpenAI** | Remoto | 💰 Pago | 🔴 Baixa | 🟢 Excelente |
| **Anthropic** | Remoto | 💰 Pago | 🔴 Baixa | 🟢 Excelente |
| **Google** | Remoto | 💰 Pago | 🔴 Baixa | 🟢 Excelente |

## 🏠 Ollama (Local)

### Por que Ollama?

- **Privacidade Total**: Tudo roda na sua máquina
- **Sem Custos**: Modelos open-source gratuitos
- **Offline**: Funciona sem internet
- **Rápido**: Após download, respostas instantâneas

### Instalação

**Windows:**
```powershell
# Baixe o instalador de https://ollama.ai
# Execute o instalador
# Verifique a instalação
ollama --version
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

### Modelos Disponíveis

| Modelo | Tamanho | RAM Mín. | Descrição |
|--------|---------|----------|-----------|
| `dolphin-llama3:8b` | 4.7 GB | 8 GB | Padrão do ASTRA — companheiro sem filtros extra |
| `llama3.2` | 2 GB | 8 GB | Versão leve e rápida |
| `llama3.2:70b` | 40 GB | 64 GB | Versão completa |
| `mistral` | 4 GB | 8 GB | Ótimo para código |
| `codellama` | 4 GB | 8 GB | Especializado em programação |
| `phi` | 1.6 GB | 4 GB | Muito rápido, menor qualidade |

### Baixar Modelos

```bash
# Modelo recomendado (padrão do ASTRA)
ollama pull dolphin-llama3:8b

# Outros modelos
ollama pull llama3.2
ollama pull mistral
ollama pull codellama
ollama pull phi

# Listar modelos instalados
ollama list

# Remover modelo
ollama rm dolphin-llama3:8b
```

### Configuração

Edite `config/ai_config.yaml`:

```yaml
default_provider: ollama

providers:
  ollama:
    enabled: true
    model: dolphin-llama3:8b # Modelo a usar
    url: http://localhost:11434  # URL do servidor
    timeout: 60              # Timeout em segundos
    max_retries: 3           # Tentativas em caso de erro
```

### Testar

```python
from Astra.ai import AIEngine
import yaml

with open('config/ai_config.yaml') as f:
    config = yaml.safe_load(f)

engine = AIEngine(config)
response = engine.generate("Olá! Como você está?")
print(response.content)
```

### Troubleshooting

**Erro: "Connection refused"**
```bash
# Iniciar servidor Ollama
ollama serve
```

**Erro: "Model not found"**
```bash
# Baixar o modelo
ollama pull dolphin-llama3:8b
```

**Resposta lenta:**
```yaml
# Use modelo menor
providers:
  ollama:
    model: phi  # Mais rápido, menor qualidade
```

---

## 🌐 OpenAI

### Por que OpenAI?

- **Qualidade Superior**: GPT-4 é um dos melhores modelos
- **Sem Hardware**: Roda na nuvem
- **Setup Rápido**: Apenas API key necessária

### Custos

| Modelo | Input (por 1M tokens) | Output (por 1M tokens) |
|--------|----------------------|------------------------|
| `gpt-3.5-turbo` | $0.50 | $1.50 |
| `gpt-4` | $30.00 | $60.00 |
| `gpt-4-turbo` | $10.00 | $30.00 |

💡 **Dica**: Comece com `gpt-3.5-turbo` para testar.

### Instalação

1. **Criar Conta**
   - Acesse [platform.openai.com](https://platform.openai.com)
   - Crie uma conta
   - Adicione método de pagamento

2. **Obter API Key**
   - Vá para [API Keys](https://platform.openai.com/api-keys)
   - Clique em "Create new secret key"
   - Copie a key (só aparece uma vez!)

3. **Instalar Biblioteca**
```bash
pip install openai
```

### Configuração

**Opção 1: Variável de Ambiente (Recomendado)**

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."

# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."

# Windows CMD
set OPENAI_API_KEY=sk-...
```

Edite `config/ai_config.yaml`:
```yaml
default_provider: openai

providers:
  openai:
    enabled: true
    model: gpt-3.5-turbo
    api_key: ${OPENAI_API_KEY}  # Lê da variável de ambiente
    timeout: 60
    max_retries: 3
```

**Opção 2: Direto no Config (Menos Seguro)**

```yaml
providers:
  openai:
    enabled: true
    model: gpt-3.5-turbo
    api_key: "sk-..."  # Sua chave aqui
```

### Modelos Disponíveis

```python
# Listar modelos disponíveis
from openai import OpenAI

client = OpenAI(api_key="sua-chave")
models = client.models.list()
for model in models.data:
    print(model.id)
```

### Controlar Custos

```yaml
providers:
  openai:
    model: gpt-3.5-turbo  # Modelo mais barato
    
defaults:
  max_tokens: 500  # Limitar resposta
  temperature: 0.7

# Ativar cache para evitar requisições duplicadas
cache_enabled: true
cache_ttl: 3600
```

### Troubleshooting

**Erro: "Invalid API key"**
- Verifique se copiou a key completa
- Verifique se a variável de ambiente está configurada

**Erro: "Rate limit exceeded"**
- Aguarde alguns minutos
- Considere upgrade no plano OpenAI

**Custo muito alto:**
- Use `gpt-3.5-turbo` em vez de `gpt-4`
- Ative cache
- Limite `max_tokens`

---

## 🔄 Fallback Entre Provedores

Configure fallback automático para máxima confiabilidade:

```yaml
default_provider: ollama

providers:
  ollama:
    enabled: true
    model: dolphin-llama3:8b
  
  openai:
    enabled: true
    model: gpt-3.5-turbo
    api_key: ${OPENAI_API_KEY}

# Se Ollama falhar, tenta OpenAI
fallback_chain:
  - ollama
  - openai
```

### Como Funciona

1. Astra tenta primeiro o `default_provider` (Ollama)
2. Se falhar (modelo não encontrado, servidor offline, etc.)
3. Automaticamente tenta o próximo na `fallback_chain` (OpenAI)
4. Se todos falharem, retorna erro

### Exemplo de Uso

```python
# Mesmo código funciona com qualquer provedor
response = engine.generate("Olá!")

# Metadados mostram qual provedor foi usado
print(f"Provedor: {response.provider}")
print(f"Modelo: {response.model}")

# Se foi fallback
if response.metadata.get('is_fallback'):
    print(f"Fallback de {response.metadata['original_provider']}")
```

---

## 🎛️ Parâmetros Avançados

### Temperature

Controla criatividade vs precisão:

```yaml
defaults:
  temperature: 0.0  # Muito determinístico (bom para fatos)
  temperature: 0.7  # Balanceado (padrão)
  temperature: 1.0  # Muito criativo (bom para ideias)
```

### Max Tokens

Limita tamanho da resposta:

```yaml
defaults:
  max_tokens: null   # Sem limite
  max_tokens: 500    # ~375 palavras
  max_tokens: 1000   # ~750 palavras
```

### System Prompt

Define comportamento da IA:

```yaml
defaults:
  system_prompt: |
    Você é o Astra, um assistente técnico especializado.
    Responda sempre em português de Portugal.
    Seja conciso e direto ao ponto.
```

---

## 🔐 Segurança

### Boas Práticas

✅ **Faça:**
- Use variáveis de ambiente para API keys
- Adicione `config/*.yaml` ao `.gitignore`
- Rotacione API keys regularmente
- Use Ollama para dados sensíveis

❌ **Não Faça:**
- Commitar API keys no Git
- Compartilhar API keys
- Usar mesma key em múltiplos projetos

### Exemplo de .gitignore

```gitignore
# API Keys e configurações sensíveis
config/ai_config.yaml
config/skills_config.yaml
.env
*.key
```

---

## 📊 Comparação de Uso

### Para Desenvolvimento

**Recomendação**: Ollama (dolphin-llama3:8b)
- Grátis
- Privado
- Rápido para testar

### Para Produção (Uso Leve)

**Recomendação**: Ollama + OpenAI (fallback)
```yaml
fallback_chain:
  - ollama      # 99% das requisições
  - openai      # Backup quando Ollama falha
```

### Para Produção (Alta Qualidade)

**Recomendação**: OpenAI (gpt-4)
- Melhor qualidade
- Mais confiável
- Suporte empresarial

---

## 🆘 Precisa de Ajuda?

- **Documentação Ollama**: [ollama.ai/docs](https://ollama.ai/docs)
- **Documentação OpenAI**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Issues**: [GitHub Issues](https://github.com/Renonemre-oss/astra-assistant/issues)

---

**💡 Dica Final**: Comece com Ollama para aprender e testar. Quando estiver confortável, adicione OpenAI como fallback para máxima confiabilidade!



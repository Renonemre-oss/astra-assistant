# 🤖 Jarvis AI Assistant - Projeto Reorganizado

Um assistente de IA avançado com capacidades multimodais, incluindo reconhecimento de voz, síntese de fala, análise contextual e personalidade adaptativa.

## ✅ Reorganização Completa

Este projeto foi completamente reorganizado para melhor estrutura e manutenibilidade:

### 🔄 Principais Mudanças

- **✅ Estrutura Unificada**: Consolidação de arquivos duplicados
- **✅ Organização Modular**: Separação clara de responsabilidades
- **✅ Configurações Centralizadas**: Sistema de configuração unificado
- **✅ Documentação Estruturada**: Documentação organizada por categorias
- **✅ Testes Consolidados**: Todos os testes em estrutura única
- **✅ Scripts Organizados**: Scripts utilitários em local apropriado

## 📁 Nova Estrutura

```
jarvis/                          # 🔥 PROJETO ORGANIZADO
├── core/                        # 🧠 Código principal do assistente
│   ├── assistant.py            # Classe principal do assistente
│   └── __version__.py          # Informações de versão
├── modules/                     # 🔧 Módulos funcionais organizados
│   ├── audio/                  # Gerenciamento de áudio
│   ├── database/               # Banco de dados e modelos
│   ├── speech/                 # Reconhecimento e síntese de fala
│   ├── ui/                     # Interface de usuário
│   ├── *.py                    # Módulos individuais consolidados
├── api/                        # 🌐 Integrações de API
├── voice/                      # 🎤 Identificação e processamento de voz
├── neural_models/              # 🧠 Modelos de machine learning
├── utils/                      # 🛠️ Utilitários e ferramentas
├── config/                     # ⚙️ Configurações organizadas
│   ├── settings/               # Configurações principais
│   ├── templates/              # Templates de configuração
│   └── backup/                 # Backups de configuração
├── data/                       # 💾 Dados organizados por categoria
│   ├── models/                 # Modelos treinados
│   ├── user/                   # Dados do usuário
│   ├── conversation/           # Histórico de conversas
│   ├── personality/            # Dados de personalidade
│   ├── companion/              # Configurações do companion
│   ├── memory/                 # Sistema de memória
│   ├── contextual_analysis/    # Análises contextuais
│   └── voice_*/               # Dados relacionados à voz
├── tests/                      # 🧪 Testes consolidados
├── scripts/                    # 📜 Scripts utilitários
├── examples/                   # 📝 Exemplos e demos
└── docs/                       # 📚 Documentação estruturada
    ├── api/                    # Documentação de APIs
    ├── guides/                 # Guias de uso
    └── architecture/           # Documentação de arquitetura
```

## 🚀 Como Usar o Projeto Reorganizado

### 1. Navegação
```bash
cd jarvis_organized/jarvis
```

### 2. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 3. Execução Principal
```bash
python main.py  # Anteriormente run_alex.py
```

### 4. Interface Gráfica
```bash
python scripts/gui_launcher.py
```

### 5. Testes
```bash
python -m pytest tests/
```

## 🔄 Migração dos Dados

Os dados foram preservados e organizados:

- **✅ Configurações**: Mantidas em `config/`
- **✅ Dados do usuário**: Preservados em `data/user/`
- **✅ Histórico**: Mantido em `data/conversation/`
- **✅ Modelos**: Consolidados em `neural_models/`
- **✅ Personalidade**: Organizada em `data/personality/`

## 📋 Benefícios da Reorganização

### 🎯 **Estrutura Clara**
- Separação lógica de componentes
- Fácil navegação no projeto
- Redução de arquivos duplicados

### 🔧 **Manutenibilidade**
- Código mais organizado
- Dependências claras entre módulos
- Configurações centralizadas

### 📚 **Documentação**
- Estrutura hierárquica da documentação
- Guias específicos por funcionalidade
- Exemplos organizados

### 🧪 **Testes**
- Todos os testes em uma estrutura unificada
- Fácil execução e manutenção
- Cobertura organizada

## 🔗 Arquivos Importantes

### 📋 **Configuração Principal**
- `config/settings/main_config.py` - Configuração principal
- `config/settings/voice_config.json` - Configuração de voz
- `config/settings/speech_config.json` - Configuração de fala

### 🚀 **Execução**
- `main.py` - Ponto de entrada principal (ex-run_alex.py)
- `scripts/gui_launcher.py` - Interface gráfica
- `scripts/voice_mode.py` - Modo apenas voz

### 🧠 **Core**
- `core/assistant.py` - Assistente principal
- `modules/` - Todos os módulos funcionais
- `neural_models/` - Modelos de IA

## 🛠️ Scripts Disponíveis

```bash
# Limpeza do sistema
python scripts/cleanup.py

# Configuração do banco de dados  
python scripts/setup_database.py

# Visualização de logos
python scripts/show_logos.py

# Inicialização (Windows)
scripts/start_jarvis.bat
```

## 📖 Documentação

A documentação foi reorganizada e está disponível em:

- **`docs/guides/`** - Guias de uso e configuração
- **`docs/api/`** - Documentação das APIs
- **`docs/architecture/`** - Documentação técnica e arquitetura

### 📑 **Guias Disponíveis**
- `docs/guides/VOICE_TRAINING_GUIDE.md`
- `docs/guides/CONFIGURAR_ELEVENLABS.md`  
- `docs/guides/HOTWORD_SETUP_GUIDE.md`
- `docs/guides/AUDIO_VISUALIZATION_GUIDE.md`

## ⚠️ Importante

### 🔄 **Backup Realizado**
O projeto original permanece intacto. Esta é uma versão reorganizada e melhorada.

### 🎯 **Próximos Passos**
1. Testar a nova estrutura
2. Ajustar imports se necessário
3. Verificar funcionamento de todos os módulos
4. Atualizar documentação específica

## 🤝 **Contribuição**

Com a nova estrutura, contribuições ficaram mais organizadas:

1. **Core Changes**: `core/` e `modules/`
2. **API Changes**: `api/`
3. **UI Changes**: `modules/ui/`
4. **Documentation**: `docs/`
5. **Tests**: `tests/`

---

## 🧠 Sistema RAG (Retrieval-Augmented Generation)

### ✨ Novo: Memória Semântica Inteligente!

O ALEX/JARVIS agora possui sistema RAG que permite:

- 🔍 **Busca Semântica**: Encontra informações por significado, não apenas palavras-chave
- 💾 **Memória de Longo Prazo**: Lembra conversas anteriores semanticamente
- 📚 **Aprendizado com Documentos**: Processa PDFs, TXT, MD
- 🤖 **Contexto Enriquecido**: Gera respostas mais informadas

### 📦 Componentes RAG

- **`jarvis/ai/vector_store.py`** - ChromaDB para embeddings
- **`jarvis/ai/embeddings_manager.py`** - Sentence Transformers
- **`jarvis/ai/document_processor.py`** - Processamento de documentos
- **`jarvis/ai/rag_system.py`** - Sistema RAG integrado
- **`jarvis/modules/rag_memory_integration.py`** - Integração com memória

### 🚀 Uso Rápido

```bash
# Instalar dependências RAG
pip install chromadb sentence-transformers PyPDF2

# Executar exemplo
python examples/rag_example.py
python examples/rag_memory_example.py
```

### 📖 Documentação

Veja `docs/RAG.md` para documentação completa do sistema RAG.

---

## 🎉 **Projeto Pronto para Uso!**

A reorganização está completa e o projeto está pronto para desenvolvimento contínuo com uma estrutura muito mais limpa e organizada.

### 🔥 **Destaques da Reorganização:**
- ✅ Zero arquivos duplicados
- ✅ Estrutura modular clara  
- ✅ Configurações centralizadas
- ✅ Documentação organizada
- ✅ Testes consolidados
- ✅ Scripts em local apropriado
- ✅ **Sistema RAG Integrado** (v3.0)
- ✅ **Memória Semântica** (v3.0)

**🚀 Happy coding com a nova estrutura organizada!**

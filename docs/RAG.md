# Sistema RAG - Retrieval-Augmented Generation

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Componentes](#componentes)
3. [Instalação](#instalação)
4. [Uso Básico](#uso-básico)
5. [Exemplos Avançados](#exemplos-avançados)
6. [API Reference](#api-reference)
7. [Melhores Práticas](#melhores-práticas)

---

## 🎯 Visão Geral

O sistema **RAG (Retrieval-Augmented Generation)** permite que o ALEX/JARVIS:

- 🧠 **Aprenda com documentos** (PDF, TXT, MD)
- 🔍 **Busque semanticamente** em conversas e documentos
- 💾 **Armazene embeddings** para recuperação eficiente
- 🤖 **Gere contexto enriquecido** para LLMs

### Benefícios

- **Memória de Longo Prazo**: Lembra de conversas anteriores
- **Aprendizado Contextual**: Aprende com documentação
- **Busca Inteligente**: Encontra informações por significado, não apenas palavras-chave
- **Respostas Informadas**: Gera respostas baseadas em conhecimento específico

---

## 🔧 Componentes

### 1. Vector Store (`vector_store.py`)
Armazena embeddings usando **ChromaDB**.

**Características:**
- Persistência em disco
- Busca por similaridade vetorial
- Suporte a metadados
- Filtros avançados

### 2. Embeddings Manager (`embeddings_manager.py`)
Gera embeddings usando **Sentence Transformers**.

**Modelo Padrão:** `all-MiniLM-L6-v2`
- Dimensão: 384
- Velocidade: Alta
- Qualidade: Boa para uso geral

### 3. Document Processor (`document_processor.py`)
Processa documentos em chunks.

**Formatos Suportados:**
- PDF (`.pdf`)
- Texto (`.txt`)
- Markdown (`.md`)

**Processamento:**
- Chunking inteligente (quebra em sentenças)
- Sobreposição configurável
- Metadados automáticos

### 4. RAG System (`rag_system.py`)
Integra todos os componentes.

**Funcionalidades:**
- Adicionar documentos e textos
- Busca semântica
- Geração de contexto
- Salvar conversas
- Estatísticas do sistema

---

## 📦 Instalação

### Dependências Principais

```bash
pip install chromadb sentence-transformers PyPDF2
```

### Dependências Completas

Adicione ao `requirements.txt`:

```txt
# RAG - Retrieval Augmented Generation
chromadb==0.5.23          # Vector database
sentence-transformers==3.3.1  # Embeddings
PyPDF2==3.0.1             # PDF processing
```

### Instalação Completa

```bash
# Ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

---

## 🚀 Uso Básico

### Inicialização

```python
from jarvis.ai import get_rag_system

# Obter instância global
rag = get_rag_system()

# Verificar status
stats = rag.get_stats()
print(f"Ready: {stats['ready']}")
```

### Adicionar Conhecimento

```python
# Adicionar texto diretamente
rag.add_text(
    "Python é uma linguagem de programação interpretada.",
    metadata={'category': 'programming'}
)

# Adicionar documento
from pathlib import Path
rag.add_document(Path("manual.pdf"))

# Adicionar diretório
rag.add_directory(Path("docs/"))
```

### Busca Semântica

```python
# Busca simples
results = rag.search("O que é Python?", n_results=5)

for result in results:
    print(f"Relevância: {1-result['distance']:.2%}")
    print(f"Texto: {result['document']}")
    print(f"Fonte: {result['metadata'].get('source', 'N/A')}")
```

### Gerar Contexto para LLM

```python
# Gerar contexto enriquecido
query = "Como criar APIs com Python?"
context = rag.generate_context(
    query, 
    n_results=3,
    max_context_length=2000
)

# Usar com LLM
prompt = f"""
Contexto:
{context}

Pergunta: {query}

Resposta:
"""
```

### Salvar Conversas

```python
# Adicionar conversa ao RAG
rag.add_conversation(
    user_message="Qual é o seu nome?",
    assistant_response="Meu nome é ALEX!",
    metadata={'timestamp': '2024-01-01'}
)

# Buscar conversas antigas
results = rag.search("qual é o nome do assistente")
```

---

## 💡 Exemplos Avançados

### Exemplo 1: Processar Documentação

```python
from pathlib import Path
from jarvis.ai import get_rag_system

rag = get_rag_system()

# Processar toda documentação
docs_dir = Path("project_docs/")
count = rag.add_directory(docs_dir)
print(f"✅ Processados {count} chunks")

# Consultar documentação
results = rag.search("Como configurar o sistema?")

for i, result in enumerate(results[:3], 1):
    print(f"\n[{i}] {result['metadata']['source']}")
    print(f"    {result['document'][:200]}...")
```

### Exemplo 2: Base de Conhecimento Customizada

```python
# Carregar conhecimentos específicos
conhecimentos = [
    {
        "text": "O comando 'git commit' salva mudanças no repositório.",
        "metadata": {"category": "git", "difficulty": "basic"}
    },
    {
        "text": "O comando 'git rebase' reescreve o histórico de commits.",
        "metadata": {"category": "git", "difficulty": "advanced"}
    }
]

for k in conhecimentos:
    rag.add_text(k["text"], metadata=k["metadata"])

# Buscar por dificuldade
results = rag.search(
    "comandos git",
    filters={"difficulty": "basic"}
)
```

### Exemplo 3: Integração com Assistant

```python
from jarvis.ai import get_rag_system

class SmartAssistant:
    def __init__(self):
        self.rag = get_rag_system()
    
    def process_message(self, user_message: str) -> str:
        # Buscar contexto relevante
        context = self.rag.generate_context(
            user_message, 
            n_results=3
        )
        
        # Gerar resposta (integrar com LLM)
        if context:
            prompt = f"Contexto:\n{context}\n\nPergunta: {user_message}"
            response = self.generate_response(prompt)
        else:
            response = self.generate_response(user_message)
        
        # Salvar conversa para futuro
        self.rag.add_conversation(user_message, response)
        
        return response
    
    def generate_response(self, prompt: str) -> str:
        # Integrar com seu LLM preferido
        pass
```

---

## 📚 API Reference

### RAGSystem

#### `__init__(vector_store, embeddings_manager, document_processor)`
Inicializa sistema RAG.

**Parâmetros:**
- `vector_store` (VectorStore, optional): Vector store customizado
- `embeddings_manager` (EmbeddingsManager, optional): Embeddings manager customizado
- `document_processor` (DocumentProcessor, optional): Document processor customizado

#### `add_text(text: str, metadata: dict) -> bool`
Adiciona texto ao sistema.

**Parâmetros:**
- `text`: Texto para adicionar
- `metadata`: Metadados opcionais

**Retorna:** `True` se sucesso

#### `add_document(file_path: Path) -> bool`
Adiciona documento ao sistema.

**Parâmetros:**
- `file_path`: Caminho do arquivo (.pdf, .txt, .md)

**Retorna:** `True` se sucesso

#### `add_directory(directory: Path) -> int`
Adiciona todos os documentos de um diretório.

**Parâmetros:**
- `directory`: Diretório com documentos

**Retorna:** Número de chunks adicionados

#### `search(query: str, n_results: int, filters: dict) -> List[dict]`
Busca semântica.

**Parâmetros:**
- `query`: Texto de busca
- `n_results`: Número de resultados (padrão: 5)
- `filters`: Filtros de metadata (opcional)

**Retorna:** Lista de resultados com `document`, `metadata`, `distance`, `id`

#### `generate_context(query: str, n_results: int, max_context_length: int) -> str`
Gera contexto para LLM.

**Parâmetros:**
- `query`: Pergunta do usuário
- `n_results`: Número de documentos (padrão: 3)
- `max_context_length`: Tamanho máximo em caracteres (padrão: 2000)

**Retorna:** Contexto formatado

#### `add_conversation(user_message: str, assistant_response: str, metadata: dict) -> bool`
Adiciona conversa ao sistema.

**Parâmetros:**
- `user_message`: Mensagem do usuário
- `assistant_response`: Resposta do assistente
- `metadata`: Metadados adicionais (opcional)

**Retorna:** `True` se sucesso

#### `clear() -> bool`
Limpa todos os dados do RAG.

**Retorna:** `True` se sucesso

#### `get_stats() -> dict`
Retorna estatísticas do sistema.

**Retorna:** Dict com `vector_store`, `embeddings`, `ready`

---

## ✅ Melhores Práticas

### Performance

1. **Batch Processing**: Adicione múltiplos documentos de uma vez
2. **Chunk Size**: Ajuste baseado no tipo de conteúdo (500-1000 caracteres)
3. **Filtros**: Use metadados para buscas mais eficientes

### Qualidade

1. **Limpeza de Texto**: Remova ruído antes de adicionar
2. **Metadados Ricos**: Adicione contexto útil (data, autor, categoria)
3. **Testes de Busca**: Valide resultados regularmente

### Segurança

1. **Validação de Entrada**: Verifique documentos antes de processar
2. **Sanitização**: Remova informações sensíveis
3. **Backups**: Faça backup do vector store periodicamente

### Escalabilidade

1. **Persistência**: Use diretório persistente para ChromaDB
2. **Indexação**: Adicione documentos offline quando possível
3. **Limpeza**: Remova documentos antigos ou irrelevantes

---

## 🔄 Fluxo Típico

```
1. Inicializar RAG
   ↓
2. Carregar Documentação
   ↓
3. Usuário faz pergunta
   ↓
4. RAG busca contexto relevante
   ↓
5. LLM gera resposta com contexto
   ↓
6. Salvar conversa no RAG
   ↓
7. Repetir 3-6
```

---

## 📊 Configuração do Sistema

### Chunk Size

```python
from jarvis.ai import DocumentProcessor

# Customizar processador
processor = DocumentProcessor(
    chunk_size=800,      # Maior para documentos técnicos
    chunk_overlap=100    # Mais sobreposição
)
```

### Modelo de Embeddings

```python
from jarvis.ai import EmbeddingsManager

# Usar modelo diferente
embeddings = EmbeddingsManager(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"  # Multilíngue
)
```

### Persistência

```python
from jarvis.ai import VectorStore
from pathlib import Path

# Diretório customizado
vector_store = VectorStore(
    persist_directory=Path("/data/vector_store")
)
```

---

## 🐛 Troubleshooting

### ChromaDB não inicializa

```bash
# Reinstalar ChromaDB
pip uninstall chromadb
pip install chromadb==0.5.23
```

### Modelo de embeddings não carrega

```bash
# Baixar modelo manualmente
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### PDFs não processam

```bash
# Verificar PyPDF2
pip install --upgrade PyPDF2
```

---

## 📈 Monitoramento

```python
# Estatísticas do sistema
stats = rag.get_stats()

print(f"Vector Store:")
print(f"  - Disponível: {stats['vector_store']['available']}")
print(f"  - Total docs: {stats['vector_store']['total_documents']}")

print(f"Embeddings:")
print(f"  - Modelo: {stats['embeddings']['model_name']}")
print(f"  - Dimensão: {stats['embeddings']['embedding_dim']}")

print(f"Sistema: {'✅ Pronto' if stats['ready'] else '❌ Não pronto'}")
```

---

## 🔗 Links Úteis

- [ChromaDB Docs](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [PyPDF2 Docs](https://pypdf2.readthedocs.io/)
- [RAG Paper](https://arxiv.org/abs/2005.11401)

---

**Versão:** 3.0  
**Última Atualização:** Dezembro 2024

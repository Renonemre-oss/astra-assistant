# astra/

Pacote principal do **ASTRA** — Assistente Pessoal com Inteligência Afetiva.

A documentação completa (funcionalidades, instalação, configuração e arquitetura) está no [README principal](../README.md), na raiz do projeto.

## Execução

```bash
# a partir da raiz do projeto, com o ambiente virtual ativo:
python -m astra
```

## Organização do pacote

| Diretório | Conteúdo |
|---|---|
| `core/` | Ponto de entrada da aplicação (`assistant.py`) |
| `modules/` | Motores afetivo, de decisão, de memória, voz, UI, base de dados |
| `ai/` | RAG, embeddings e providers de LLM (Ollama / OpenAI) |
| `api_server/` | API REST (FastAPI) |
| `config/` | Constantes, feature flags e ficheiros de configuração |
| `skills/`, `plugins/` | Frameworks extensíveis |
| `security/` | Autenticação, encriptação, rate limiting |
| `utils/` | Utilitários partilhados |
| `data/` | Dados de runtime (não versionados) |
| `tests/` | Testes unitários e de integração |

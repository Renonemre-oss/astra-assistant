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
| `security/` | Autenticação, encriptação, rate limiting (ver nota abaixo) |
| `utils/` | Utilitários partilhados |
| `data/` | Dados de runtime (não versionados) |
| `tests/` | Testes unitários e de integração |

> `security/` e `api_server/` só interessam se um dia expuseres o ASTRA para lá do teu PC (ex: acesso remoto via telemóvel). O servidor REST não arranca sozinho nem tem autenticação ligada por padrão.

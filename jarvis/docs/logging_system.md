# Sistema de Logging do ALEX

## Visão Geral

O ALEX possui um sistema de logging centralizado que registra todas as atividades importantes do sistema em arquivo e no console.

## Configuração

### Localização dos Logs
- **Diretório:** `logs/`
- **Arquivo principal:** `alex_assistant.log`
- **Encoding:** UTF-8 (suporte completo a emojis e caracteres especiais)

### Função de Configuração

A função `configure_logging()` em `config/config.py` é responsável por:
- Criar handlers para arquivo e console
- Configurar encoding UTF-8 para suporte completo a caracteres especiais
- Definir formato de mensagens com timestamp
- Configurar nível de logging (INFO por padrão)

## Como Usar

### 1. Inicialização

O logging é configurado automaticamente nos arquivos principais:

```python
from config.config import configure_logging
configure_logging()
```

### 2. Em Módulos do Sistema

```python
import logging

# Obter logger
logger = logging.getLogger(__name__)

# Usar diferentes níveis
logger.debug("Mensagem de debug")
logger.info("Operação realizada com sucesso")
logger.warning("Situação que requer atenção")
logger.error("Erro durante operação")
logger.critical("Erro crítico do sistema")
```

### 3. Exemplos de Uso

```python
# Log de inicialização
logger.info("🚀 ALEX iniciado com sucesso")

# Log de operações
logger.info("✅ Base de dados conectada")
logger.warning("⚠️ Tesseract não encontrado")
logger.error("❌ Falha na conexão")

# Log com contexto
logger.info(f"📄 Conversa criada: ID={conversation_id}")
```

## Níveis de Log

| Nível | Uso | Exemplo |
|-------|-----|---------|
| DEBUG | Informações detalhadas para debug | Valores de variáveis, fluxo detalhado |
| INFO | Operações normais do sistema | Inicializações, operações completadas |
| WARNING | Situações anômalas mas não críticas | Serviços indisponíveis, fallbacks |
| ERROR | Erros que afetam funcionalidade | Falhas de conexão, erros de processamento |
| CRITICAL | Erros que podem parar o sistema | Falhas críticas, corrupção de dados |

## Formato das Mensagens

```
2025-09-19 16:17:56,412 - INFO - 🚀 ALEX iniciado com sucesso
```

**Estrutura:**
- `YYYY-MM-DD HH:MM:SS,mmm` - Timestamp completo
- `LEVEL` - Nível do log
- `Mensagem` - Conteúdo da mensagem (com suporte a emojis)

## Integração com Módulos

### run_alex.py
- Configura logging no início da execução
- Garante que todos os módulos herdem a configuração

### core/assistente.py
- Usa logging para todas as operações principais
- Logs de inicialização, conexões, erros

### Outros Módulos
- Cada módulo pode usar `logging.getLogger(__name__)` 
- Herda automaticamente a configuração central

## Benefícios

1. **Centralizado:** Uma única configuração para todo o sistema
2. **Consistente:** Formato uniforme em todos os logs
3. **UTF-8:** Suporte completo a emojis e caracteres especiais
4. **Dupla saída:** Console (desenvolvimento) + arquivo (persistência)
5. **Flexível:** Fácil ajuste de níveis e formatos

## Manutenção

### Rotação de Logs
Para implementar rotação automática de logs:

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    LOGS_DIR / 'alex_assistant.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
```

### Limpeza
Os logs são mantidos no diretório `logs/` e podem ser limpos periodicamente se necessário.

## Troubleshooting

### Problema: Caracteres especiais não aparecem
**Solução:** Verificar se a configuração UTF-8 está ativa

### Problema: Logs duplicados
**Solução:** A configuração limpa handlers existentes automaticamente

### Problema: Arquivo não é criado
**Solução:** Verificar se o diretório `logs/` existe e tem permissões de escrita
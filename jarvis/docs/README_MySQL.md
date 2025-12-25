# 🗄️ ALEX - Integração MySQL com HeidiSQL

O assistente ALEX agora suporta gravação completa de conversas numa base de dados MySQL, permitindo histórico persistente e análise detalhada das interações.

## 🚀 **CONFIGURAÇÃO INICIAL**

### **1. Pré-requisitos**
- ✅ MySQL Server instalado e a funcionar
- ✅ HeidiSQL instalado
- ✅ Python com `mysql-connector-python`

### **2. Setup da Base de Dados**
Execute o script de configuração:
```bash
python setup_database.py
```

Este script irá:
- 🔧 Configurar a conexão MySQL
- 🏗️ Criar a base de dados `alex_assistant`
- 📋 Criar todas as tabelas necessárias  
- 💾 Gerar ficheiro de configuração `mysql_config.ini`
- 📱 Mostrar instruções para HeidiSQL

### **3. Estrutura da Base de Dados**

#### **📊 Tabelas Criadas:**

**`conversations`** - Dados das conversas
- `id` - ID único da conversa
- `session_id` - ID da sessão (único)
- `title` - Título da conversa
- `personality` - Personalidade usada
- `created_at` / `updated_at` - Timestamps
- `metadata` - Dados adicionais (JSON)

**`messages`** - Mensagens trocadas
- `id` - ID único da mensagem
- `conversation_id` - Referência à conversa
- `message_type` - 'user', 'assistant' ou 'system'
- `content` - Conteúdo da mensagem
- `timestamp` - Quando foi enviada
- `response_time` - Tempo de resposta (segundos)
- `model_used` - Modelo usado (ex: "gemma3n:e4b")
- `metadata` - Metadados (JSON)

**`voice_interactions`** - Interações por voz
- `conversation_id` - Referência à conversa
- `audio_duration` - Duração do áudio
- `recognition_confidence` - Confiança do reconhecimento
- `tts_enabled` - Se TTS estava ativo

**`user_preferences`** - Preferências do utilizador
- `preference_key` - Chave da preferência
- `preference_value` - Valor da preferência
- `data_type` - Tipo de dados

## 🔍 **USANDO HEIDISQL**

### **1. Conectar ao MySQL**
1. Abrir HeidiSQL
2. Criar Nova Sessão:
   - **Tipo**: MySQL (TCP/IP) 
   - **Host**: localhost
   - **Porta**: 3306
   - **Utilizador**: root (ou seu utilizador)
   - **Password**: [sua password]

### **2. Consultas Úteis**

#### **📈 Estatísticas Gerais**
```sql
-- Total de conversas
SELECT COUNT(*) as total_conversas FROM conversations WHERE is_active = TRUE;

-- Total de mensagens
SELECT COUNT(*) as total_mensagens FROM messages;

-- Mensagens por tipo
SELECT message_type, COUNT(*) as quantidade 
FROM messages 
GROUP BY message_type;
```

#### **💬 Histórico de Conversas**
```sql
-- Últimas 10 conversas
SELECT id, title, personality, created_at, updated_at
FROM conversations 
ORDER BY updated_at DESC 
LIMIT 10;

-- Mensagens de uma conversa específica
SELECT message_type, content, timestamp, response_time
FROM messages 
WHERE conversation_id = 1 
ORDER BY timestamp;
```

#### **🔍 Pesquisa de Conteúdo**
```sql
-- Buscar mensagens contendo palavra-chave
SELECT c.title, m.message_type, m.content, m.timestamp
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE m.content LIKE '%palavra-chave%'
ORDER BY m.timestamp DESC;

-- Busca full-text (mais eficiente)
SELECT c.title, m.message_type, m.content, m.timestamp
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE MATCH(m.content) AGAINST('termo de busca' IN NATURAL LANGUAGE MODE);
```

#### **⏱️ Análise de Performance**
```sql
-- Tempo médio de resposta por conversa
SELECT c.title, AVG(m.response_time) as tempo_medio_resposta
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE m.response_time IS NOT NULL
GROUP BY c.id, c.title
ORDER BY tempo_medio_resposta DESC;

-- Distribuição de tempos de resposta
SELECT 
    CASE 
        WHEN response_time < 1 THEN '< 1s'
        WHEN response_time < 5 THEN '1-5s'
        WHEN response_time < 10 THEN '5-10s'
        ELSE '> 10s'
    END as faixa_tempo,
    COUNT(*) as quantidade
FROM messages 
WHERE response_time IS NOT NULL
GROUP BY faixa_tempo;
```

#### **📊 Personalidades Mais Usadas**
```sql
SELECT personality, COUNT(*) as quantidade
FROM conversations 
WHERE is_active = TRUE
GROUP BY personality 
ORDER BY quantidade DESC;
```

## ⚙️ **FUNCIONALIDADES**

### **🔄 Funcionamento Automático**
- ✅ **Conexão automática** ao iniciar o assistente
- ✅ **Gravação transparente** de todas as mensagens
- ✅ **Fallback gracioso** se MySQL não estiver disponível
- ✅ **Histórico persistente** entre sessões
- ✅ **Metadados completos** (tempo resposta, modelo usado, etc.)

### **💾 Backup e Manutenção**
```sql
-- Backup de uma conversa específica
SELECT * FROM messages WHERE conversation_id = 1 
INTO OUTFILE '/path/to/backup_conversa_1.csv'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n';

-- Limpeza de conversas antigas (mais de 30 dias)
DELETE FROM conversations 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### **🚨 Resolução de Problemas**

#### **Erro de Conexão**
1. Verificar se MySQL Server está a funcionar
2. Confirmar credenciais no `mysql_config.ini`
3. Executar novamente `setup_database.py`

#### **Tabelas Não Encontradas**
```sql
-- Recriar estrutura manualmente se necessário
USE alex_assistant;
SHOW TABLES;
```

#### **Performance Lenta**
```sql
-- Adicionar índices se necessário
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_content ON messages(content);
```

## 📈 **BENEFÍCIOS**

- 🔍 **Busca avançada** em todo o histórico
- 📊 **Análises detalhadas** de uso e performance  
- 💾 **Backup automático** de todas as conversas
- 🔄 **Sincronização** entre diferentes sessões
- 📱 **Visualização profissional** com HeidiSQL
- ⚡ **Performance otimizada** com índices MySQL

---

**🎉 Agora pode gerir completamente o histórico do ALEX através do HeidiSQL!**
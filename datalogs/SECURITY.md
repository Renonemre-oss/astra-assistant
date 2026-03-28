# 🔒 ALEX/JARVIS - Guia de Segurança

## 📋 Índice
- [Visão Geral](#visão-geral)
- [Quick Start](#quick-start)
- [Componentes de Segurança](#componentes)
- [Boas Práticas](#boas-práticas)
- [Configuração](#configuração)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O ALEX/JARVIS implementa múltiplas camadas de segurança:

- 🔐 **Secrets Manager** - Gestão segura de API keys
- 🔑 **JWT Authentication** - Autenticação token-based
- ⏱️ **Rate Limiting** - Proteção contra abuse
- 🛡️ **Data Encryption** - Encriptação de dados sensíveis

---

## ⚡ Quick Start

### 1. Instalar Dependências de Segurança

```bash
pip install cryptography python-dotenv pyjwt
```

### 2. Configurar .env

```bash
# Copiar template
cp .env.example .env

# Gerar JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Editar .env

```bash
# Preencher variáveis obrigatórias
JWT_SECRET_KEY=<seu_token_gerado>
OLLAMA_API_URL=http://localhost:11434
DATABASE_PATH=data/jarvis.db
```

---

## 🔧 Componentes

### 1️⃣ Secrets Manager

**Localização:** `jarvis/security/secrets_manager.py`

**Uso Básico:**
```python
from security import get_secret

# Obter API key
api_key = get_secret('NEWSDATA_API_KEY')

# Verificar status
from security import get_secret_manager
sm = get_secret_manager()
status = sm.get_status()
```

**Features:**
- ✅ Carregamento automático de .env
- ✅ Encriptação em memória
- ✅ Validação de secrets obrigatórios
- ✅ Audit log de acessos

---

### 2️⃣ Authentication (JWT)

**Localização:** `jarvis/security/authentication.py`

**Uso Básico:**
```python
from security import get_auth_manager

auth = get_auth_manager()

# Criar token
token = auth.create_access_token(username='user', role='admin')

# Verificar token
user = auth.get_current_user(token)
if user:
    print(f"Autenticado: {user.username}")
```

**Integração com FastAPI:**
```python
from fastapi import Depends, HTTPException, Header
from security import get_auth_manager

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, "Token inválido")
    
    token = authorization.split(' ')[1]
    user = get_auth_manager().get_current_user(token)
    
    if not user:
        raise HTTPException(401, "Token expirado")
    
    return user

# Usar em endpoint
@app.get("/protected")
async def protected_endpoint(user = Depends(get_current_user)):
    return {"message": f"Hello {user.username}"}
```

---

### 3️⃣ Rate Limiting

**Localização:** `jarvis/security/rate_limiter.py`

**Uso Básico:**
```python
from security import rate_limit

# Verificar limite
allowed, retry_after = rate_limit(key='user_ip', rule='api')

if not allowed:
    print(f"Rate limit! Tente novamente em {retry_after}s")
```

**Regras Disponíveis:**
- `default`: 60 req/min
- `api`: 100 req/min
- `auth`: 5 req/min (login)
- `strict`: 10 req/min

**Integração com FastAPI:**
```python
from fastapi import Request, HTTPException
from security import rate_limit

async def rate_limit_middleware(request: Request):
    client_ip = request.client.host
    
    allowed, retry_after = rate_limit(client_ip, 'api')
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit excedido. Tente em {retry_after}s"
        )
```

---

### 4️⃣ Data Encryption

**Localização:** `jarvis/security/encryption.py`

**Uso Básico:**
```python
from security import encrypt_data, decrypt_data

# Encriptar
encrypted = encrypt_data("dados sensíveis")

# Decriptar
original = decrypt_data(encrypted)
```

**Encriptação Customizada:**
```python
from security import DataEncryptor

# Criar encriptação com password
encryptor = DataEncryptor.from_password("minha_senha_forte")

# Encriptar
encrypted = encryptor.encrypt("dados")

# Decriptar
decrypted = encryptor.decrypt(encrypted)
```

---

## ✅ Boas Práticas

### 1. Gestão de Secrets

❌ **NÃO FAZER:**
```python
# NÃO hardcode API keys!
api_key = "abc123def456"
```

✅ **FAZER:**
```python
# Use Secrets Manager
from security import get_secret
api_key = get_secret('API_KEY')
```

---

### 2. Autenticação

❌ **NÃO FAZER:**
```python
# NÃO use senhas em plain text
if password == "admin123":
    login()
```

✅ **FAZER:**
```python
# Use JWT tokens
from security import get_auth_manager

token = auth.create_access_token(username)
```

---

### 3. Rate Limiting

✅ **SEMPRE aplicar em:**
- Endpoints de login/auth
- APIs públicas
- Endpoints com operações custosas

```python
@app.post("/login")
async def login(request: Request):
    # Rate limit no login
    allowed, _ = rate_limit(request.client.host, 'auth')
    if not allowed:
        raise HTTPException(429, "Muitas tentativas")
```

---

### 4. Dados Sensíveis

✅ **Encriptar:**
- Senhas de usuário
- Tokens de refresh
- Dados pessoais
- Chaves privadas

```python
# Encriptar antes de salvar no DB
encrypted_password = encrypt_data(password)
db.save(encrypted_password)
```

---

## 🔧 Configuração Avançada

### Alterar Tempo de Expiração JWT

```python
# Em security/authentication.py
auth = AuthenticationManager()
auth.access_token_expire = 120  # 2 horas
auth.refresh_token_expire = 30  # 30 dias
```

### Customizar Rate Limits

```python
from security import get_rate_limiter

limiter = get_rate_limiter()
limiter.rules['custom'] = RateLimitRule(
    max_requests=200,
    window_seconds=60,
    name='custom'
)
```

### Usar Encriptação Custom

```python
from security import DataEncryptor

# Gerar nova chave
from cryptography.fernet import Fernet
key = Fernet.generate_key()

# Usar chave específica
encryptor = DataEncryptor(key=key)
```

---

## 🐛 Troubleshooting

### Erro: "cryptography não instalado"

```bash
pip install cryptography
```

### Erro: "PyJWT não instalado"

```bash
pip install pyjwt
```

### JWT Token Inválido

1. Verificar secret key está correto
2. Verificar token não expirou
3. Testar geração de novo token

### Rate Limit Muito Restritivo

```python
# Resetar contador
from security import get_rate_limiter
get_rate_limiter().reset('chave_do_usuario')
```

---

## 📊 Monitoring de Segurança

### Ver Status de Secrets

```python
from security import get_secret_manager

sm = get_secret_manager()
status = sm.get_status()

print(f"Secrets: {status['total_secrets']}")
print(f"Válidos: {status['is_valid']}")
print(f"Encriptação: {status['encryption_enabled']}")
```

### Ver Stats de Rate Limiting

```python
from security import get_rate_limiter

stats = get_rate_limiter().get_stats()
print(f"Chaves ativas: {stats['active_keys']}")
print(f"Requests tracked: {stats['total_requests_tracked']}")
```

---

## 🚨 Em Caso de Comprometimento

1. **Revogar todos os tokens**
2. **Gerar novo JWT_SECRET_KEY**
3. **Rotacionar API keys**
4. **Verificar logs de acesso**
5. **Atualizar senhas**

```bash
# Gerar nova chave
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Atualizar .env
JWT_SECRET_KEY=<nova_chave>

# Reiniciar aplicação
```

---

## 📚 Referências

- [JWT.io](https://jwt.io/) - JWT Documentation
- [Cryptography Docs](https://cryptography.io/) - Python Cryptography
- [OWASP](https://owasp.org/) - Security Best Practices

---

## ✅ Checklist de Segurança

- [ ] .env configurado corretamente
- [ ] .env adicionado ao .gitignore
- [ ] JWT_SECRET_KEY gerado aleatoriamente
- [ ] API keys não hardcoded no código
- [ ] Rate limiting aplicado em endpoints sensíveis
- [ ] Dados sensíveis encriptados
- [ ] Logs de segurança habilitados
- [ ] Backup de secrets configurado

---

**Última atualização:** 25/12/2024
**Versão:** 1.0.0

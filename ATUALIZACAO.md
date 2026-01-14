# 🔄 Guia de Atualização do Jarvis

Este guia explica como atualizar o Jarvis de forma segura e eficiente.

---

## 📋 Índice

1. [Métodos de Atualização](#métodos-de-atualização)
2. [Atualização Manual](#atualização-manual)
3. [Atualização Automática](#atualização-automática)
4. [Gerenciamento de Backups](#gerenciamento-de-backups)
5. [Solução de Problemas](#solução-de-problemas)

---

## 🎯 Métodos de Atualização

O Jarvis oferece **3 formas de atualização**:

### 1. Interface Gráfica (Recomendado para iniciantes)
```bash
python update_jarvis.py
```

### 2. Linha de Comando (Para usuários avançados)
```bash
# Verificar atualizações
python update_jarvis.py --check

# Atualizar automaticamente
python update_jarvis.py --update

# Criar backup
python update_jarvis.py --backup

# Ver configuração
python update_jarvis.py --config
```

### 3. Programática (Para desenvolvedores)
```python
from utils.auto_updater import get_updater

updater = get_updater()
update_info = updater.check_for_updates()

if update_info:
    update_file = updater.download_update(update_info)
    if update_file:
        updater.install_update(update_file)
```

---

## 🔧 Atualização Manual

### Passo a Passo

#### 1. Abrir o Update Manager
```bash
python update_jarvis.py
```

#### 2. Menu Principal
```
============================================================
MENU PRINCIPAL
============================================================

1. Verificar atualizações
2. Atualizar agora
3. Configurar atualização automática
4. Gerenciar backups
5. Criar backup manual
0. Sair
```

#### 3. Verificar Atualizações (Opção 1)
- Mostra se há nova versão disponível
- Exibe notas de lançamento
- Indica tamanho do download

#### 4. Atualizar (Opção 2)
- Baixa a atualização
- Cria backup automático
- Instala e pede para reiniciar

---

## 🤖 Atualização Automática

### Configurar (Menu → Opção 3)

```
⚙️ CONFIGURAÇÃO DE ATUALIZAÇÃO AUTOMÁTICA
------------------------------------------------------------

1. Verificação automática: ✅ Ativada
2. Download automático: ❌ Desativado
3. Instalação automática: ❌ Desativada
4. Intervalo de verificação: 24h
5. Canal de atualização: stable
```

### Opções Disponíveis

| Opção | Descrição | Recomendado |
|-------|-----------|-------------|
| **Verificação automática** | Verifica se há atualizações | ✅ Ativado |
| **Download automático** | Baixa atualizações automaticamente | ❌ Desativado |
| **Instalação automática** | Instala sem confirmação | ❌ Desativado |

### Canais de Atualização

- **stable** (padrão): Versões estáveis e testadas
- **beta**: Versões em teste, com novas funcionalidades
- **dev**: Versões de desenvolvimento (instável)

### Intervalo de Verificação

Defina cada quanto tempo verificar:
- **Mínimo**: 1 hora
- **Recomendado**: 24 horas
- **Máximo**: 168 horas (7 dias)

---

## 💾 Gerenciamento de Backups

### Por Que Backups São Importantes?

- ✅ Proteção contra falhas na atualização
- ✅ Possibilidade de reverter mudanças
- ✅ Segurança dos seus dados e configurações

### Backups Automáticos

O Jarvis **cria backup automaticamente** antes de cada atualização.

### Backups Manuais

#### Criar Backup Manual (Menu → Opção 5)
```
💾 Criando backup...
✅ Backup criado: jarvis_backup_v2.0.0_20251225_173000.zip
```

#### Listar Backups (Menu → Opção 4)
```
💾 BACKUPS DISPONÍVEIS
------------------------------------------------------------
1. jarvis_backup_v2.0.0_20251225_173000.zip
   Tamanho: 15.3 MB | Data: 2025-12-25 17:30:00

2. jarvis_backup_v2.0.0_20251224_120000.zip
   Tamanho: 14.8 MB | Data: 2025-12-24 12:00:00
```

### Restaurar Backup

1. Ir para "Gerenciar backups" (Opção 4)
2. Escolher número do backup
3. Confirmar restauração
4. Reiniciar o Jarvis

### Limpeza de Backups

O sistema **mantém automaticamente os últimos 5 backups** e remove os mais antigos.

---

## 🔄 Processo de Atualização Completo

### Fluxo Visual

```
[Verificar] → [Nova versão?] → [Download] → [Backup] → [Instalar] → [Reiniciar]
      ↓              |             ↓           ↓          ↓           ↓
    Não          Não há        Progresso    Automático  Aplicar    Pronto
                                 █████░░░                 
```

### Etapas Detalhadas

#### 1. Verificação (30 segundos)
- Conecta ao servidor de atualizações
- Compara versões
- Baixa informações da release

#### 2. Download (1-5 minutos)
- Baixa arquivo .zip
- Mostra barra de progresso
- Verifica integridade

#### 3. Backup (30 segundos - 2 minutos)
- Compacta arquivos atuais
- Salva em `.backups/`
- Remove backups antigos

#### 4. Instalação (1-2 minutos)
- Extrai novos arquivos
- Substitui arquivos antigos
- Mantém configurações e dados

#### 5. Reinício
- Fechar Jarvis
- Abrir novamente
- Nova versão carregada!

---

## 📊 Versionamento Semântico

O Jarvis usa **versionamento semântico** (X.Y.Z):

### Formato: MAJOR.MINOR.PATCH

- **MAJOR (X)**: Mudanças incompatíveis (ex: 1.0.0 → 2.0.0)
- **MINOR (Y)**: Novas funcionalidades compatíveis (ex: 2.0.0 → 2.1.0)
- **PATCH (Z)**: Correções de bugs (ex: 2.0.0 → 2.0.1)

### Exemplos

```
v1.0.0  ────┐
            │ Patch (correção)
v1.0.1  ────┤
            │ Minor (nova funcionalidade)
v1.1.0  ────┤
            │ Major (breaking change)
v2.0.0  ────┘
```

---

## ⚠️ Solução de Problemas

### "Erro ao verificar atualizações"

**Causa**: Sem conexão com internet ou servidor offline

**Solução**:
```bash
# Verificar conexão
ping github.com

# Forçar verificação
python update_jarvis.py --check
```

### "Falha ao criar backup"

**Causa**: Espaço insuficiente em disco

**Solução**:
1. Verificar espaço disponível
2. Limpar arquivos temporários
3. Tentar novamente

### "Erro ao instalar atualização"

**Causa**: Permissões insuficientes ou arquivos em uso

**Solução**:
1. Fechar o Jarvis completamente
2. Executar como Administrador (Windows)
3. Restaurar backup se necessário

### "Jarvis não inicia após atualização"

**Solução**:
```bash
# 1. Restaurar backup
python update_jarvis.py
# Menu → 4 → Escolher backup → Confirmar

# 2. Verificar logs
cat logs/alex_assistant.log

# 3. Reinstalar dependências
pip install -r requirements.txt
```

---

## 🛡️ Segurança

### Verificações Realizadas

- ✅ **Checksum**: Integridade do download
- ✅ **HTTPS**: Conexão segura
- ✅ **Backup automático**: Antes de cada instalação
- ✅ **Rollback**: Possibilidade de voltar atrás

### Boas Práticas

1. **Sempre criar backup antes** de atualizar
2. **Ler notas de lançamento** para saber o que mudou
3. **Testar em ambiente de desenvolvimento** primeiro
4. **Manter backups recentes** salvos separadamente
5. **Não interromper** o processo de atualização

---

## 📝 Comandos Rápidos

### Verificar versão atual
```bash
python jarvis/main.py --version
```

### Verificar atualizações
```bash
python update_jarvis.py --check
```

### Atualizar automaticamente
```bash
python update_jarvis.py --update
```

### Criar backup
```bash
python update_jarvis.py --backup
```

### Ver configuração
```bash
python update_jarvis.py --config
```

---

## 🔗 Configuração do Servidor de Atualizações

### Para Desenvolvedores

Edite `jarvis/utils/auto_updater.py`:

```python
class JarvisUpdater:
    # Altere estas URLs para seu repositório
    UPDATE_SERVER = "https://api.github.com/repos/SEU_USERNAME/jarvis"
    RELEASES_URL = f"{UPDATE_SERVER}/releases/latest"
```

### Criar Release no GitHub

1. **Tag a versão**:
```bash
git tag v2.0.1
git push origin v2.0.1
```

2. **Criar release**:
- Ir para GitHub → Releases → New Release
- Escolher tag (v2.0.1)
- Adicionar notas de lançamento
- Anexar arquivo .zip do Jarvis
- Publicar!

3. **O Jarvis detecta automaticamente** a nova versão

---

## 📞 Suporte

Se encontrar problemas:

1. **Verificar logs**: `logs/alex_assistant.log`
2. **Restaurar backup**: Menu → Opção 4
3. **Reportar issue**: GitHub Issues
4. **Documentação**: `docs/` folder

---

## ✨ Changelog

### v2.0.0 (Atual)
- ✨ Sistema de atualização automática
- 💾 Backups automáticos
- 🔒 Verificação de integridade
- 🎨 Interface de gerenciamento
- 📊 Versionamento semântico

---

**🎉 Mantenha seu Jarvis sempre atualizado!**

*Última atualização: 25 de Dezembro de 2025*

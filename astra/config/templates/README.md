# 📁 Templates - Assistente ASTRA

Esta pasta contém templates padronizados para facilitar o desenvolvimento de novos módulos e funcionalidades no assistente ASTRA.

## 📋 **Templates Disponíveis**

### 🐍 `module_template.py`
Template base para criar novos módulos Python:
- ✅ Estrutura padrão de classe
- ✅ Logging configurado
- ✅ Tratamento de erros
- ✅ Validação de configurações
- ✅ Sistema de status
- ✅ Métodos de inicialização e finalização
- ✅ Documentação completa

**Como usar:**
1. Copie `module_template.py` para `modules/`
2. Renomeie para `seu_modulo.py`
3. Adapte a classe e métodos conforme necessário
4. Implemente a lógica específica em `_process_logic()`

### ⚙️ `config_template.json`
Template de configuração JSON para módulos:
- ✅ Estrutura padronizada
- ✅ Seções organizadas (settings, features, api, etc.)
- ✅ Parâmetros comuns pré-definidos
- ✅ Comentários explicativos

**Como usar:**
1. Copie `config_template.json` para `config/`
2. Renomeie para `seu_modulo_config.json`
3. Adapte os parâmetros conforme necessário
4. Reference no seu módulo via `config_loader`

## 🚀 **Exemplo de Uso Rápido**

```bash
# 1. Copiar template
cp templates/module_template.py modules/meu_novo_modulo.py
cp templates/config_template.json config/meu_novo_modulo_config.json

# 2. Editar arquivo
# Substitua "ModuleTemplate" por "MeuNovoModulo"
# Implemente sua lógica específica

# 3. Testar
python modules/meu_novo_modulo.py
```

## 🎯 **Padrões e Convenções**

### **Nomenclatura**
- **Módulos:** `snake_case.py` (ex: `voice_cloning.py`)
- **Classes:** `PascalCase` (ex: `VoiceCloning`)
- **Configs:** `modulo_config.json`

### **Estrutura de Módulo**
```python
class MeuModulo:
    def __init__(self, config):
        # Inicialização
        
    def _validate_config(self):
        # Validação de configurações
        
    def _setup_module(self):
        # Configuração específica
        
    def process(self, input_data):
        # Lógica principal
        
    def get_status(self):
        # Status do módulo
```

### **Logging**
Todos os módulos devem usar o sistema de logging padrão:
```python
import logging
logger = logging.getLogger(__name__)

# Uso
logger.info("Informação")
logger.error("Erro")
logger.debug("Debug")
```

## 📚 **Recursos Adicionais**

- **Documentação:** `docs/guides/`
- **Exemplos:** `tests/examples/`
- **Utilitários:** `utils/`

## 🔧 **Desenvolvimento**

Ao criar novos templates:
1. Mantenha compatibilidade com estrutura existente
2. Inclua documentação completa
3. Adicione exemplos de uso
4. Teste templates antes de commitar

---

**🚀 Templates para desenvolvimento mais rápido e consistente!**

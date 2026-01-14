# 💛 Sistema de Memória Emocional do ASTRA

## 🎯 Filosofia: Emoção NUNCA Existe Sozinha

O sistema de memória emocional do ASTRA foi projetado com uma regra fundamental:

> **💡 Emoções sempre devem estar associadas a um contexto específico**

Isso evita que o assistente acumule "bagagem emocional" de bugs, mal-entendidos ou interações isoladas.

---

## 🔑 Regras Fundamentais

### 1. Contexto Obrigatório

Toda memória emocional **DEVE** ter pelo menos um destes contextos:

- **Evento**: O que aconteceu (ex: "Ajudei o usuário com problema urgente")
- **Pessoa**: Com quem foi a interação (ex: "João", "Maria")
- **Contexto Temporal**: Quando aconteceu (sempre adicionado automaticamente)

### 2. Decay Agressivo

Memórias emocionais têm **vida útil curta de propósito**:

```python
# Memórias emocionais
emotional_decay_rate = 0.15  # 15% decay por dia (AGRESSIVO)
meia_vida = ~5 dias

# Memórias normais
normal_decay_rate = 0.05     # 5% decay por dia
meia_vida = ~7 dias
```

**Por quê?**
- Evita que bugs causem "ressentimento" permanente
- Previne acumulação de ruído emocional
- Mantém o ASTRA responsivo ao contexto atual

### 3. Reforço Limitado

Quando uma memória emocional é acessada:
- **Emocionais**: +5% reforço (limitado)
- **Normais**: +10% reforço (padrão)

Isso impede que emoções antigas dominem o comportamento.

---

## 📊 Arquitetura do Sistema

### Fluxo de Processamento

```
Input → Context Analyzer
      → Personality Modulator
      → Intent Router
         → Skill OR LLM
      → Response Formatter
      → Audio / UI
         ↓
      Memory System
         ↓
      Emotional Context Validation
         ↓
      Storage with Decay
```

### Validação de Memória Emocional

```python
class MemoryEntry:
    def _validate_emotional_memory(self, emotions, context):
        """
        REGRA CRÍTICA: Emoção NUNCA existe sozinha!
        - Precisa de evento (o que aconteceu)
        - Precisa de pessoa (com quem foi)
        - Precisa de contexto temporal (quando foi)
        """
        if emotions and not context:
            raise ValueError(
                "❌ Memória emocional sem contexto! "
                "Emoções devem estar associadas a evento, pessoa ou contexto temporal."
            )
```

---

## 🛠️ Como Usar Corretamente

### ✅ Forma Correta

```python
# 1. Método Especializado (RECOMENDADO)
memory_system.store_emotional_memory(
    content="Usuário me agradeceu muito",
    emotions=['happy', 'grateful'],
    event="Ajudei com problema urgente do trabalho",
    person="João"
)

# 2. Via store_conversation_turn (automático)
memory_system.store_conversation_turn(
    user_input="Muito obrigado, você me salvou!",
    assistant_response="Fico feliz em ajudar!",
    user_emotions=['grateful', 'relieved'],
    context={
        'event': 'Resolução de problema técnico',
        'person': 'João',
        'companion_type': 'friend'
    }
)
```

### ❌ Forma Incorreta

```python
# NUNCA FAÇA ISSO!
memory_system.store_memory(
    content="Usuário estava feliz",
    memory_type=MemoryType.EMOTIONAL,
    emotions=['happy'],
    context={}  # ❌ SEM CONTEXTO!
)
# Resultado: ValueError ou contexto mínimo adicionado automaticamente
```

---

## 🧹 Limpeza Automática

### Cleanup de Memórias Emocionais

```python
# Remover memórias emocionais com mais de 7 dias
removed = memory_system.cleanup_old_emotional_memories(days_threshold=7)

# Configuração recomendada: executar diariamente
# Via cron job ou scheduler interno
```

### Health Check

```python
health = memory_system._assess_memory_health()

print(f"Status: {health['status']}")
print(f"Score: {health['score']}/100")
print(f"Memórias emocionais: {health['emotional_memories']}")
print(f"Ratio emocional: {health['emotional_ratio']}")

# ⚠️ Alerta se emotional_ratio > 0.3 (30%)
if health['emotional_ratio'] > 0.3:
    print("⚠️ Excesso de memórias emocionais - executar limpeza!")
```

---

## 📈 Decay Temporal

### Como Funciona

```python
# Cálculo de decay acumulado
days_ago = (current_time - memory_time).days
accumulated_decay = decay_factor * (1 - emotional_decay_rate) ** days_ago

# Exemplo: Memória emocional de 5 dias atrás
# Day 0: 1.0
# Day 1: 0.85
# Day 2: 0.72
# Day 3: 0.61
# Day 4: 0.52
# Day 5: 0.44  # Menos de 50% da força original!

# Memória normal de 5 dias atrás
# Day 0: 1.0
# Day 1: 0.95
# Day 2: 0.90
# Day 3: 0.86
# Day 4: 0.81
# Day 5: 0.77  # Ainda 77% da força original
```

### Score de Relevância

```python
final_score = (
    base_importance * 0.3 +
    content_match * 0.4 +
    tag_match * 0.1 +
    temporal_score * 0.1 +  # Inclui decay acumulado
    access_score * 0.1
)
```

---

## 🔬 Casos de Uso

### 1. Gratidão do Usuário

```python
# Contexto: Usuário agradece após ajuda
memory_system.store_emotional_memory(
    content="Usuário expressou gratidão profunda",
    emotions=['grateful', 'happy'],
    event="Resolvi problema crítico no deadline",
    person="João"
)
```

### 2. Frustração Técnica

```python
# Contexto: Problema técnico causa frustração
memory_system.store_emotional_memory(
    content="Usuário frustrado com erro recorrente",
    emotions=['frustrated', 'stressed'],
    event="Bug no sistema persistiu por 3 dias",
    person="Maria"
)
# ⚠️ Esta memória decairá rapidamente (5 dias)
# Evita que o ASTRA fique "ressentido" se o bug foi corrigido
```

### 3. Momento de Aprendizado

```python
# Contexto: Usuário aprende algo novo
memory_system.store_emotional_memory(
    content="Usuário teve insight importante",
    emotions=['excited', 'surprised'],
    event="Descobriu nova feature do Python",
    person="Carlos"
)
```

---

## ⚙️ Configuração Avançada

### Ajustar Rates de Decay

```python
# No momento da criação da memória
memory = MemoryEntry(
    content="...",
    memory_type=MemoryType.EMOTIONAL,
    emotions=['happy']
)

# Padrões automáticos:
# - Emocionais: emotional_decay_rate = 0.15
# - Normais: emotional_decay_rate = 0.05

# Para ajustar manualmente (não recomendado):
memory.emotional_decay_rate = 0.20  # Decay ainda mais agressivo
```

### Threshold de Limpeza

```python
# Configuração do sistema
memory_system = MemorySystem()

# Limpeza agressiva: 5 dias
memory_system.cleanup_old_emotional_memories(days_threshold=5)

# Limpeza moderada: 10 dias
memory_system.cleanup_old_emotional_memories(days_threshold=10)

# Limpeza conservadora: 14 dias
memory_system.cleanup_old_emotional_memories(days_threshold=14)
```

---

## 🎭 Integração com Personality Engine

### Fluxo Completo

```python
# 1. Personality Engine detecta emoção do usuário
user_mood = personality_engine.analyze_user_mood(user_input)

# 2. Memory System armazena com contexto rico
memory_system.store_conversation_turn(
    user_input=user_input,
    assistant_response=response,
    user_emotions=[user_mood.value],
    context={
        'event': f"Conversa sobre {topic}",
        'person': current_user,
        'companion_type': companion_engine.current_companion_type,
        'time_context': personality_engine.get_time_context().value
    }
)

# 3. Próxima interação usa memórias relevantes
relevant_context = memory_system.get_relevant_context(new_input)
# ✅ Memórias emocionais antigas já terão decaído
```

---

## 📊 Métricas de Saúde

### Indicadores Importantes

| Métrica | Ótimo | Bom | Atenção | Crítico |
|---------|-------|-----|---------|---------|
| `emotional_ratio` | < 0.2 | 0.2-0.3 | 0.3-0.4 | > 0.4 |
| `health_score` | > 80 | 60-80 | 40-60 | < 40 |
| Memórias emocionais > 7 dias | 0 | < 10 | 10-20 | > 20 |

### Alertas Automáticos

```python
def check_emotional_health():
    health = memory_system._assess_memory_health()
    
    if health['emotional_ratio'] > 0.4:
        logger.warning("🚨 Excesso crítico de memórias emocionais!")
        memory_system.cleanup_old_emotional_memories(days_threshold=5)
    
    elif health['emotional_ratio'] > 0.3:
        logger.warning("⚠️ Alto nível de memórias emocionais")
        memory_system.cleanup_old_emotional_memories(days_threshold=7)
```

---

## 🔍 Debug e Diagnóstico

### Inspecionar Memórias Emocionais

```python
# Listar todas as memórias emocionais
emotional_memories = [
    mem for mem in memory_system.memories.values()
    if mem.emotions and len(mem.emotions) > 0
]

for mem in emotional_memories:
    print(f"ID: {mem.id}")
    print(f"Emoções: {mem.emotions}")
    print(f"Contexto: {mem.context}")
    print(f"Decay: {mem.decay_factor:.2f}")
    print(f"Idade: {(datetime.now() - datetime.fromisoformat(mem.timestamp)).days} dias")
    print("---")
```

### Verificar Contexto de Memória

```python
def validate_emotional_memory(memory: MemoryEntry):
    """Verifica se memória emocional está bem formada"""
    
    if not memory.emotions:
        return True  # Não é emocional
    
    required_keys = ['event', 'person', 'temporal_context', 'time_context']
    has_context = any(key in memory.context for key in required_keys)
    
    if not has_context:
        logger.error(f"⚠️ Memória {memory.id} emocional sem contexto adequado!")
        return False
    
    return True
```

---

## 🚀 Best Practices

### ✅ DO's

1. **Sempre use `store_emotional_memory()` para emoções explícitas**
2. **Forneça evento específico e pessoa quando possível**
3. **Execute limpeza emocional regularmente (diariamente)**
4. **Monitore `emotional_ratio` - mantenha < 0.3**
5. **Use contexto rico do CompanionEngine**

### ❌ DON'Ts

1. **Nunca armazene emoção sem contexto**
2. **Não acumule memórias emocionais por semanas**
3. **Não aumente `emotional_decay_rate` acima de 0.20**
4. **Não ignore avisos de health check**
5. **Não use memórias emocionais para fatos objetivos**

---

## 📚 Referências

- `memory_system.py`: Implementação completa
- `personality_engine.py`: Detecção de emoções
- `companion_engine.py`: Contexto emocional rico
- `assistant.py`: Integração no fluxo principal

---

**Versão**: 2.0  
**Data**: Janeiro 2026  
**Status**: ✅ Implementado e Testado

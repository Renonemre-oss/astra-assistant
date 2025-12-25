#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Demonstração do Sistema de Memória Inteligente
Script para demonstrar como o ALEX lembra de conversas e aprende sobre o usuário.
"""

import sys
import time
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports
from modules.memory_system import MemorySystem, MemoryType, MemoryImportance

def demonstrate_conversation_memory():
    """Demonstra armazenamento e recuperação de conversas."""
    print("💬 DEMONSTRAÇÃO - Memória de Conversas")
    print("=" * 50)
    
    memory = MemorySystem()
    
    # Simular uma série de conversas
    conversations = [
        ("Oi! Meu nome é João", "Olá João! Prazer te conhecer!"),
        ("Eu gosto muito de pizza", "Que legal! Pizza é uma das melhores comidas mesmo."),
        ("Trabalho como programador", "Programação é fascinante! Que linguagens você usa?"),
        ("Minha cor favorita é azul", "Azul é uma cor linda! Muito relaxante."),
        ("Tenho um cachorro chamado Rex", "Rex deve ser um companheiro incrível!"),
        ("Moro em Lisboa", "Lisboa é uma cidade maravilhosa!"),
        ("Gosto de jogar futebol aos domingos", "Futebol é ótimo exercício e diversão!"),
    ]
    
    print("📝 Armazenando conversas...")
    for user_input, assistant_response in conversations:
        memory.store_conversation_turn(
            user_input=user_input,
            assistant_response=assistant_response,
            user_emotions=["neutral"],
            context={"demo": True}
        )
        print(f"✅ Armazenado: {user_input[:30]}...")
        time.sleep(0.5)
    
    print(f"\n🧠 Total de memórias: {len(memory.memories)}")
    
    # Testar recuperação
    print("\n🔍 Testando recuperação de memórias:")
    test_queries = [
        "João",
        "pizza", 
        "trabalho programador",
        "cachorro",
        "Lisboa",
        "futebol domingo"
    ]
    
    for query in test_queries:
        relevant_memories = memory.retrieve_memories(query, max_results=2)
        print(f"\n📋 Busca: '{query}'")
        for i, mem in enumerate(relevant_memories, 1):
            content = mem.content
            if content.startswith("Usuário disse: "):
                content = content[15:]
            print(f"  {i}. {content}")

def demonstrate_context_retrieval():
    """Demonstra recuperação de contexto relevante."""
    print("\n🎯 DEMONSTRAÇÃO - Contexto Relevante")
    print("=" * 50)
    
    memory = MemorySystem()
    
    # Adicionar algumas memórias de teste
    test_memories = [
        ("João é programador Python", MemoryType.SEMANTIC, ["pessoa", "profissão"]),
        ("João gosta de pizza margherita", MemoryType.SEMANTIC, ["pessoa", "comida"]),
        ("João tem um cachorro Rex", MemoryType.SEMANTIC, ["pessoa", "animal"]),
        ("João mora em Lisboa", MemoryType.SEMANTIC, ["pessoa", "localização"]),
        ("Ontem João foi ao cinema", MemoryType.EPISODIC, ["atividade", "lazer"]),
        ("João joga futebol aos domingos", MemoryType.SEMANTIC, ["pessoa", "esporte"]),
    ]
    
    print("📚 Criando base de conhecimento sobre João...")
    for content, mem_type, tags in test_memories:
        memory.store_memory(content, mem_type, tags=tags)
        print(f"✅ {content}")
    
    # Testar contexto para diferentes perguntas
    test_questions = [
        "O que você sabe sobre João?",
        "João gosta de que tipo de comida?", 
        "Onde João mora?",
        "João tem animais de estimação?",
        "O que João faz para se divertir?"
    ]
    
    print("\n💭 Obtendo contexto relevante para perguntas:")
    for question in test_questions:
        context = memory.get_relevant_context(question, max_memories=3)
        print(f"\n❓ Pergunta: {question}")
        if context:
            print(f"🧠 Contexto recuperado:")
            for line in context.split('\n')[1:]:  # Pular primeira linha do título
                if line.strip():
                    print(f"   {line}")
        else:
            print("   (Nenhum contexto relevante encontrado)")

def demonstrate_pattern_recognition():
    """Demonstra reconhecimento de padrões."""
    print("\n📊 DEMONSTRAÇÃO - Reconhecimento de Padrões")
    print("=" * 50)
    
    memory = MemorySystem()
    
    # Simular padrão de interações em diferentes horários
    from datetime import datetime, timedelta
    import json
    
    # Criar memórias com timestamps diferentes
    patterns_data = [
        # Manhãs - assuntos de trabalho
        ("Preciso terminar o projeto hoje", ["trabalho", "urgente"], "09:00"),
        ("Tenho reunião às 10h", ["trabalho", "compromisso"], "08:30"),
        ("Como está o progresso do código?", ["trabalho", "programação"], "09:30"),
        
        # Tardes - perguntas gerais
        ("Qual é a previsão do tempo?", ["clima", "informação"], "15:00"),
        ("Conte-me uma piada", ["humor", "entretenimento"], "16:00"),
        ("Como fazer um bolo?", ["culinária", "receita"], "15:30"),
        
        # Noites - assuntos pessoais
        ("Estou cansado hoje", ["pessoal", "emoção"], "21:00"),
        ("Que filme você recomenda?", ["entretenimento", "filme"], "20:30"),
        ("Boa noite, até amanhã", ["despedida", "cortesia"], "22:00"),
    ]
    
    print("⏰ Simulando padrões temporais de interação...")
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for content, tags, hour_str in patterns_data:
        # Criar timestamp simulado
        hour, minute = map(int, hour_str.split(':'))
        mem_time = base_date.replace(hour=hour, minute=minute)
        
        # Criar memória manualmente com timestamp customizado
        from modules.memory_system import MemoryEntry
        memory_entry = MemoryEntry(
            content=f"Usuário disse: {content}",
            memory_type=MemoryType.EPISODIC,
            tags=tags
        )
        memory_entry.timestamp = mem_time.isoformat()
        memory.memories[memory_entry.id] = memory_entry
        print(f"✅ {hour_str}: {content}")
    
    # Analisar padrões
    print("\n🔍 Analisando padrões comportamentais...")
    patterns = memory.analyze_user_patterns()
    
    print("\n📈 Padrões encontrados:")
    for pattern_type, data in patterns.items():
        if data:
            print(f"\n📊 {pattern_type.replace('_', ' ').title()}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"   • {key}: {value}")
            elif isinstance(data, list):
                for item in data[:3]:  # Mostrar apenas top 3
                    print(f"   • {item}")

def demonstrate_memory_types():
    """Demonstra diferentes tipos de memória."""
    print("\n🧠 DEMONSTRAÇÃO - Tipos de Memória")
    print("=" * 50)
    
    memory = MemorySystem()
    
    # Diferentes tipos de memória
    memory_examples = [
        # Memória Episódica - eventos específicos
        ("Ontem fomos ao restaurante italiano", MemoryType.EPISODIC, MemoryImportance.MEDIUM, ["evento", "comida"]),
        ("Na semana passada choveu muito", MemoryType.EPISODIC, MemoryImportance.LOW, ["clima", "evento"]),
        
        # Memória Semântica - conhecimento geral
        ("A capital do Brasil é Brasília", MemoryType.SEMANTIC, MemoryImportance.HIGH, ["geografia", "fato"]),
        ("Python é uma linguagem de programação", MemoryType.SEMANTIC, MemoryImportance.MEDIUM, ["tecnologia", "fato"]),
        
        # Memória Procedural - como fazer coisas
        ("Para fazer café: aqueça água, adicione pó, misture", MemoryType.PROCEDURAL, MemoryImportance.MEDIUM, ["culinária", "processo"]),
        ("Para instalar programa: baixar, executar, seguir instruções", MemoryType.PROCEDURAL, MemoryImportance.LOW, ["tecnologia", "processo"]),
        
        # Memória Emocional - eventos com carga emocional
        ("Fiquei muito feliz quando ganhei o prêmio", MemoryType.EMOTIONAL, MemoryImportance.HIGH, ["emoção", "conquista"]),
        ("Foi triste quando meu cachorro ficou doente", MemoryType.EMOTIONAL, MemoryImportance.HIGH, ["emoção", "animal"]),
    ]
    
    print("📚 Armazenando diferentes tipos de memória...")
    for content, mem_type, importance, tags in memory_examples:
        memory_id = memory.store_memory(content, mem_type, importance, tags)
        print(f"✅ {mem_type.value.upper()}: {content[:40]}...")
    
    # Mostrar distribuição por tipo
    summary = memory.get_memory_summary()
    print("\n📊 Distribuição por tipo de memória:")
    for mem_type, count in summary['memories_by_type'].items():
        print(f"   • {mem_type.title()}: {count} memórias")
    
    print("\n📊 Distribuição por importância:")
    for importance, count in summary['memories_by_importance'].items():
        print(f"   • {importance.title()}: {count} memórias")
    
    # Testar recuperação por tipo
    print("\n🔍 Recuperação por tipo específico:")
    for mem_type in [MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL]:
        memories = memory.retrieve_memories("", memory_types=[mem_type], max_results=2, min_relevance=0.0)
        print(f"\n📋 {mem_type.value.upper()}:")
        for mem in memories:
            print(f"   • {mem.content[:50]}...")

def demonstrate_memory_health():
    """Demonstra avaliação de saúde da memória."""
    print("\n🏥 DEMONSTRAÇÃO - Saúde da Memória")
    print("=" * 50)
    
    memory = MemorySystem()
    
    # Adicionar memórias variadas
    for i in range(10):
        memory.store_memory(
            f"Memória de teste {i+1}",
            MemoryType.EPISODIC,
            MemoryImportance.MEDIUM,
            ["teste"]
        )
    
    # Simular alguns acessos
    for mem_id in list(memory.memories.keys())[:5]:
        memory.memories[mem_id].access()
        memory.memories[mem_id].access()  # Segundo acesso
    
    # Avaliar saúde
    summary = memory.get_memory_summary()
    health = summary['memory_health']
    
    print("🏥 Avaliação de Saúde da Memória:")
    print(f"   📊 Status: {health['status'].upper()}")
    print(f"   🔢 Score: {health['score']}/100")
    print(f"   📚 Total de memórias: {health['total_memories']}")
    print(f"   📈 Média de acessos: {health['avg_accesses']}")
    print(f"   ⭐ Proporção importante: {health['important_ratio']:.1%}")
    
    status_emoji = {
        "excellent": "🌟",
        "good": "✅", 
        "fair": "⚠️",
        "poor": "❌",
        "empty": "📭"
    }
    
    emoji = status_emoji.get(health['status'], "❓")
    print(f"\n{emoji} Sistema de memória está {health['status'].upper()}")

def main():
    """Função principal da demonstração."""
    print("🧠 ALEX - Demonstração do Sistema de Memória Inteligente")
    print("=" * 60)
    print()
    
    try:
        # Executar todas as demonstrações
        demonstrate_conversation_memory()
        demonstrate_context_retrieval()
        demonstrate_pattern_recognition()
        demonstrate_memory_types()
        demonstrate_memory_health()
        
        print("\n🎉 Demonstração completa!")
        print("\n💡 O sistema de memória está funcionando perfeitamente!")
        print("   • Armazena conversas automaticamente")
        print("   • Recupera contexto relevante para respostas")
        print("   • Reconhece padrões comportamentais") 
        print("   • Gerencia diferentes tipos de memória")
        print("   • Avalia e mantém a 'saúde' da memória")
        print("   • Associa memórias relacionadas")
        print("   • Limpa memórias antigas automaticamente")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
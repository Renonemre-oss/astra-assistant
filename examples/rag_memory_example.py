#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - RAG Memory Integration Example
Demonstração da integração RAG com sistema de memória.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent / 'jarvis'
sys.path.insert(0, str(root_dir))

from modules.rag_memory_integration import get_rag_memory_integration


def demo_basic_usage():
    """Demonstração básica do sistema RAG-Memory."""
    
    print("=" * 70)
    print("🧠 ALEX/JARVIS - RAG Memory Integration Demo")
    print("=" * 70)
    
    # Obter instância
    rag_memory = get_rag_memory_integration()
    
    # Verificar status
    stats = rag_memory.get_stats()
    print(f"\n📊 Status do Sistema:")
    print(f"   Habilitado: {'✅' if stats['enabled'] else '❌'}")
    
    if not stats['enabled']:
        print(f"   Razão: {stats.get('reason', 'Unknown')}")
        print("\n⚠️ Instale dependências: pip install chromadb sentence-transformers")
        return
    
    print(f"   RAG Ready: {'✅' if stats['rag_ready'] else '❌'}")
    print(f"   Total Documentos: {stats['total_documents']}")
    print(f"   Modelo: {stats['embedding_model']}")
    
    # Exemplo 1: Salvar conversas
    print("\n" + "=" * 70)
    print("1️⃣  SALVANDO CONVERSAS COM CONTEXTO")
    print("=" * 70)
    
    conversas = [
        {
            'user': 'Qual é o seu nome?',
            'assistant': 'Meu nome é ALEX, seu assistente pessoal inteligente!',
            'context': {'emotion': 'neutral', 'topic': 'apresentação'}
        },
        {
            'user': 'Você pode me ajudar com programação Python?',
            'assistant': 'Sim! Posso ajudar com Python, desde básico até avançado.',
            'context': {'emotion': 'curious', 'topic': 'programação'}
        },
        {
            'user': 'Como criar uma função em Python?',
            'assistant': 'Use "def nome_funcao(parametros):" seguido do código indentado.',
            'context': {'emotion': 'learning', 'topic': 'python'}
        }
    ]
    
    for conv in conversas:
        success = rag_memory.save_conversation(
            user_message=conv['user'],
            assistant_response=conv['assistant'],
            context=conv['context']
        )
        if success:
            print(f"✅ Conversa salva: {conv['user'][:50]}...")
    
    # Exemplo 2: Recuperar contexto relevante
    print("\n" + "=" * 70)
    print("2️⃣  RECUPERANDO CONTEXTO RELEVANTE")
    print("=" * 70)
    
    queries = [
        "como você se chama",
        "ajuda com programação",
        "python funções"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        context = rag_memory.retrieve_context(query, n_results=2)
        
        if context:
            print("📝 Contexto recuperado:")
            print("-" * 60)
            print(context[:300] + "..." if len(context) > 300 else context)
        else:
            print("   (Sem contexto relevante)")
    
    # Exemplo 3: Buscar memórias específicas
    print("\n" + "=" * 70)
    print("3️⃣  BUSCANDO MEMÓRIAS ESPECÍFICAS")
    print("=" * 70)
    
    memories = rag_memory.search_memories(
        query="Python programação",
        n_results=3
    )
    
    print(f"\n🔍 Encontradas {len(memories)} memórias:")
    for i, memory in enumerate(memories, 1):
        doc = memory['document']
        distance = memory['distance']
        metadata = memory['metadata']
        
        print(f"\n[{i}] Relevância: {(1-distance)*100:.1f}%")
        print(f"    Tópico: {metadata.get('topic', 'N/A')}")
        print(f"    {doc[:100]}...")
    
    # Exemplo 4: Adicionar conhecimento
    print("\n" + "=" * 70)
    print("4️⃣  ADICIONANDO CONHECIMENTO")
    print("=" * 70)
    
    conhecimentos = [
        ("Python é uma linguagem interpretada e dinamicamente tipada.", "python"),
        ("FastAPI é um framework moderno para criar APIs REST.", "frameworks"),
        ("RAG combina busca com geração para respostas mais precisas.", "ai")
    ]
    
    for texto, categoria in conhecimentos:
        success = rag_memory.add_knowledge(texto, category=categoria)
        if success:
            print(f"✅ Conhecimento [{categoria}]: {texto[:60]}...")
    
    # Buscar conhecimento adicionado
    print("\n🔍 Buscando conhecimento sobre 'APIs'...")
    results = rag_memory.search_memories("criar APIs", n_results=2)
    
    for i, result in enumerate(results, 1):
        print(f"  [{i}] {result['document'][:80]}...")
    
    # Exemplo 5: Resumo de conversas
    print("\n" + "=" * 70)
    print("5️⃣  RESUMO DAS CONVERSAS")
    print("=" * 70)
    
    summary = rag_memory.get_conversation_summary(n_conversations=5)
    print(summary)
    
    # Estatísticas finais
    print("\n" + "=" * 70)
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 70)
    
    final_stats = rag_memory.get_stats()
    print(f"Total de documentos: {final_stats['total_documents']}")
    print(f"Sistema conectado: {'✅' if final_stats['memory_system_connected'] else '❌'}")
    
    print("\n✅ Demo concluído!")
    print("=" * 70)


def demo_smart_assistant():
    """Demonstração de um assistente inteligente com RAG."""
    
    print("\n" + "=" * 70)
    print("🤖 ASSISTENTE INTELIGENTE COM RAG")
    print("=" * 70)
    
    rag_memory = get_rag_memory_integration()
    
    if not rag_memory.enabled:
        print("❌ RAG não disponível")
        return
    
    print("\nSimulando conversa com memória contextual...\n")
    
    # Conversa 1
    print("👤 Usuário: Meu nome é João")
    assistant_response = "Prazer em conhecê-lo, João! Como posso ajudá-lo hoje?"
    print(f"🤖 ALEX: {assistant_response}")
    
    rag_memory.save_conversation(
        "Meu nome é João",
        assistant_response,
        context={'user_name': 'João', 'topic': 'apresentação'}
    )
    
    # Conversa 2
    print("\n👤 Usuário: Qual é o meu nome?")
    
    # Buscar contexto
    context = rag_memory.retrieve_context("qual é o meu nome", n_results=2)
    
    if "João" in context:
        response = "Seu nome é João! Me lembro de quando você se apresentou."
    else:
        response = "Você me disse que seu nome é João."
    
    print(f"🤖 ALEX: {response}")
    print(f"   [Contexto RAG usado: {'✅' if context else '❌'}]")
    
    rag_memory.save_conversation(
        "Qual é o meu nome?",
        response,
        context={'user_name': 'João', 'topic': 'memória'}
    )
    
    # Conversa 3
    print("\n👤 Usuário: Do que conversamos antes?")
    
    summary = rag_memory.get_conversation_summary(n_conversations=3)
    
    response = f"Conversamos sobre: {summary[:100]}..."
    print(f"🤖 ALEX: {response}")
    
    print("\n✅ Demonstração de assistente inteligente concluída!")


if __name__ == "__main__":
    # Executar demo básica
    demo_basic_usage()
    
    # Executar demo de assistente inteligente
    demo_smart_assistant()

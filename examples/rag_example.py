#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - RAG System Example
Exemplo de uso do sistema de Retrieval-Augmented Generation.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from jarvis.ai import get_rag_system


def main():
    """Demonstração do sistema RAG."""
    
    print("=" * 60)
    print("ALEX/JARVIS - RAG System Demo")
    print("=" * 60)
    
    # Inicializar RAG
    rag = get_rag_system()
    
    # Verificar status
    stats = rag.get_stats()
    print(f"\n📊 Status do Sistema RAG:")
    print(f"   - Vector Store: {'✅' if stats['vector_store']['available'] else '❌'}")
    print(f"   - Embeddings: {'✅' if stats['embeddings']['available'] else '❌'}")
    print(f"   - Ready: {'✅' if stats['ready'] else '❌'}")
    
    if not stats['ready']:
        print("\n❌ Sistema RAG não está pronto!")
        print("   Instale dependências: pip install chromadb sentence-transformers PyPDF2")
        return
    
    # Exemplo 1: Adicionar textos diretamente
    print("\n" + "=" * 60)
    print("1️⃣  Adicionando conhecimentos...")
    print("=" * 60)
    
    conhecimentos = [
        "Python é uma linguagem de programação interpretada de alto nível.",
        "FastAPI é um framework web moderno e rápido para construir APIs com Python.",
        "ChromaDB é um banco de dados vetorial para embeddings.",
        "RAG significa Retrieval-Augmented Generation, uma técnica que combina busca e geração."
    ]
    
    for texto in conhecimentos:
        rag.add_text(texto, metadata={'type': 'knowledge'})
    
    print(f"✅ Adicionados {len(conhecimentos)} conhecimentos")
    
    # Exemplo 2: Busca semântica
    print("\n" + "=" * 60)
    print("2️⃣  Busca Semântica")
    print("=" * 60)
    
    queries = [
        "O que é Python?",
        "Como construir APIs?",
        "O que é RAG?"
    ]
    
    for query in queries:
        print(f"\n❓ Pergunta: {query}")
        results = rag.search(query, n_results=2)
        
        if results:
            for i, result in enumerate(results, 1):
                doc = result['document']
                distance = result['distance']
                print(f"   [{i}] Relevância: {1-distance:.2%}")
                print(f"       {doc[:100]}...")
        else:
            print("   Nenhum resultado encontrado")
    
    # Exemplo 3: Gerar contexto para LLM
    print("\n" + "=" * 60)
    print("3️⃣  Geração de Contexto para LLM")
    print("=" * 60)
    
    query = "Explique como usar Python para criar APIs"
    context = rag.generate_context(query, n_results=3)
    
    print(f"\n❓ Query: {query}")
    print(f"\n📝 Contexto gerado ({len(context)} caracteres):")
    print("-" * 60)
    print(context)
    print("-" * 60)
    
    # Exemplo 4: Adicionar conversas
    print("\n" + "=" * 60)
    print("4️⃣  Salvando Conversas")
    print("=" * 60)
    
    conversas = [
        ("Qual é o seu nome?", "Meu nome é ALEX, seu assistente inteligente!"),
        ("O que você pode fazer?", "Posso ajudar com automação, programação, busca e muito mais!")
    ]
    
    for user_msg, assistant_msg in conversas:
        rag.add_conversation(user_msg, assistant_msg, metadata={'timestamp': 'now'})
    
    print(f"✅ Salvas {len(conversas)} conversas")
    
    # Buscar conversas
    print("\n🔍 Buscando conversas sobre 'nome'...")
    results = rag.search("qual é o nome do assistente", n_results=1)
    
    if results:
        print(f"✅ Encontrado:")
        print(f"   {results[0]['document']}")
    
    # Estatísticas finais
    print("\n" + "=" * 60)
    print("📊 Estatísticas Finais")
    print("=" * 60)
    
    final_stats = rag.get_stats()
    vs_stats = final_stats['vector_store']
    
    print(f"Total de documentos: {vs_stats['total_documents']}")
    print(f"Collection: {vs_stats['collection_name']}")
    
    print("\n✅ Demo completo!")
    print("=" * 60)


def test_document_processing():
    """Teste de processamento de documentos."""
    
    print("\n" + "=" * 60)
    print("5️⃣  Teste de Processamento de Documentos")
    print("=" * 60)
    
    # Criar arquivo de teste
    test_file = Path(__file__).parent / "test_document.txt"
    
    test_content = """
Este é um documento de teste para o sistema RAG.

O sistema RAG permite que o ALEX/JARVIS aprenda com documentos.
Ele pode processar PDFs, arquivos de texto e Markdown.

A busca semântica permite encontrar informações relevantes
mesmo quando as palavras exatas não são correspondidas.

Isso torna o assistente muito mais inteligente e útil.
"""
    
    # Escrever arquivo
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📄 Criado arquivo de teste: {test_file.name}")
    
    # Processar com RAG
    rag = get_rag_system()
    success = rag.add_document(test_file)
    
    if success:
        print("✅ Documento processado com sucesso")
        
        # Buscar no documento
        print("\n🔍 Buscando 'inteligente'...")
        results = rag.search("sistema inteligente", n_results=2)
        
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] Fonte: {Path(result['metadata']['source']).name}")
            print(f"    Chunk: {result['metadata']['chunk_id'] + 1}/{result['metadata']['total_chunks']}")
            print(f"    {result['document'][:150]}...")
    
    # Limpar arquivo de teste
    test_file.unlink()
    print(f"\n🗑️ Arquivo de teste removido")


if __name__ == "__main__":
    main()
    
    # Testar processamento de documentos
    test_document_processing()

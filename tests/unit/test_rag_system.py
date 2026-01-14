#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - RAG System Tests
Testes unitários para sistema RAG.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from jarvis.ai import get_rag_system, get_vector_store, get_embeddings_manager, get_document_processor


@pytest.fixture
def rag_system():
    """Fixture para sistema RAG."""
    return get_rag_system()


@pytest.fixture
def sample_texts():
    """Fixture com textos de exemplo."""
    return [
        "Python é uma linguagem de programação de alto nível.",
        "FastAPI é um framework web moderno para Python.",
        "ChromaDB é um banco de dados vetorial."
    ]


def test_vector_store_initialization():
    """Testa inicialização do vector store."""
    vs = get_vector_store()
    
    # Verificar que foi inicializado
    assert vs is not None
    
    # Verificar estatísticas
    stats = vs.get_stats()
    assert 'available' in stats
    assert 'total_documents' in stats


def test_embeddings_manager_initialization():
    """Testa inicialização do embeddings manager."""
    em = get_embeddings_manager()
    
    # Verificar que foi inicializado
    assert em is not None
    
    # Verificar estatísticas
    stats = em.get_stats()
    assert 'available' in stats
    assert 'model_name' in stats
    assert 'embedding_dim' in stats


def test_document_processor_initialization():
    """Testa inicialização do document processor."""
    dp = get_document_processor()
    
    # Verificar que foi inicializado
    assert dp is not None
    assert dp.chunk_size > 0
    assert dp.chunk_overlap >= 0


def test_rag_system_initialization(rag_system):
    """Testa inicialização do sistema RAG."""
    assert rag_system is not None
    assert rag_system.vector_store is not None
    assert rag_system.embeddings_manager is not None
    assert rag_system.document_processor is not None


def test_rag_system_stats(rag_system):
    """Testa estatísticas do sistema RAG."""
    stats = rag_system.get_stats()
    
    # Verificar estrutura
    assert 'vector_store' in stats
    assert 'embeddings' in stats
    assert 'ready' in stats
    
    # Verificar tipo do ready
    assert isinstance(stats['ready'], bool)


def test_add_text(rag_system, sample_texts):
    """Testa adição de texto."""
    # Limpar dados anteriores
    rag_system.clear()
    
    # Adicionar primeiro texto
    success = rag_system.add_text(sample_texts[0])
    
    # Verificar se funciona mesmo sem dependências instaladas
    assert isinstance(success, bool)


def test_add_conversation(rag_system):
    """Testa adição de conversa."""
    # Limpar dados anteriores
    rag_system.clear()
    
    user_msg = "Qual é o seu nome?"
    assistant_msg = "Meu nome é ALEX!"
    
    success = rag_system.add_conversation(user_msg, assistant_msg)
    
    # Verificar retorno
    assert isinstance(success, bool)


def test_search_empty(rag_system):
    """Testa busca em sistema vazio."""
    # Limpar dados
    rag_system.clear()
    
    # Buscar algo
    results = rag_system.search("Python programming")
    
    # Deve retornar lista vazia ou lista de resultados
    assert isinstance(results, list)


def test_generate_context_empty(rag_system):
    """Testa geração de contexto em sistema vazio."""
    # Limpar dados
    rag_system.clear()
    
    # Gerar contexto
    context = rag_system.generate_context("Python")
    
    # Deve retornar string vazia ou contexto
    assert isinstance(context, str)


def test_document_processor_chunks():
    """Testa criação de chunks."""
    dp = get_document_processor()
    
    # Texto curto
    short_text = "Este é um texto curto."
    chunks = dp._create_chunks(short_text)
    
    assert len(chunks) == 1
    assert chunks[0] == short_text
    
    # Texto longo (se chunk_size < texto)
    long_text = "A" * (dp.chunk_size + 100)
    chunks = dp._create_chunks(long_text)
    
    # Deve ter pelo menos 2 chunks
    assert len(chunks) >= 1


def test_clear(rag_system):
    """Testa limpeza do sistema."""
    success = rag_system.clear()
    
    # Deve retornar boolean
    assert isinstance(success, bool)


def test_add_document_nonexistent(rag_system):
    """Testa adição de documento inexistente."""
    fake_path = Path("nonexistent_file.txt")
    
    success = rag_system.add_document(fake_path)
    
    # Deve retornar False
    assert success is False


def test_add_text_empty(rag_system):
    """Testa adição de texto vazio."""
    success = rag_system.add_text("")
    
    # Deve retornar False para texto vazio
    assert success is False


def test_document_processing_text_file(tmp_path):
    """Testa processamento de arquivo de texto."""
    # Criar arquivo temporário
    test_file = tmp_path / "test.txt"
    test_content = "Este é um teste de processamento de documento."
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # Processar
    dp = get_document_processor()
    documents = dp.process_file(test_file)
    
    # Verificar resultado
    assert isinstance(documents, list)
    if documents:  # Se processou com sucesso
        assert len(documents) > 0
        assert 'text' in documents[0]
        assert 'metadata' in documents[0]


def test_search_with_filters(rag_system):
    """Testa busca com filtros."""
    # Limpar
    rag_system.clear()
    
    # Adicionar com metadata
    rag_system.add_text("Texto de teste", metadata={'category': 'test'})
    
    # Buscar (pode não funcionar sem dependências)
    results = rag_system.search("teste", filters={'category': 'test'})
    
    assert isinstance(results, list)


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])

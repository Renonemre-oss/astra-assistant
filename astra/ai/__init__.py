#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA/Astra - AI Module
Sistema de inteligência artificial com RAG e AI Engine unificado.
"""

# RAG System (já existente)
from .vector_store import VectorStore, get_vector_store
from .embeddings_manager import EmbeddingsManager, get_embeddings_manager
from .document_processor import DocumentProcessor, get_document_processor
from .rag_system import RAGSystem, get_rag_system

# AI Engine Core (novo)
from .ai_core_engine import AIEngine, CacheEntry
from .ai_providers import (
    AIProviderBase,
    AIResponse,
    AIMessage,
    ProviderStatus,
    OllamaProvider,
    OpenAIProvider
)

__all__ = [
    # RAG
    'VectorStore',
    'get_vector_store',
    'EmbeddingsManager',
    'get_embeddings_manager',
    'DocumentProcessor',
    'get_document_processor',
    'RAGSystem',
    'get_rag_system',
    # AI Engine
    'AIEngine',
    'CacheEntry',
    'AIProviderBase',
    'AIResponse',
    'AIMessage',
    'ProviderStatus',
    'OllamaProvider',
    'OpenAIProvider',
]



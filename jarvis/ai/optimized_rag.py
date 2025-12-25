#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - Optimized RAG System
Sistema RAG otimizado com cache e lazy loading.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import time

from .rag_system import RAGSystem, get_rag_system

logger = logging.getLogger(__name__)

# Tentar importar cache
try:
    from utils.cache.smart_cache import get_smart_cache, cached
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("⚠️ Smart cache não disponível")
    
    # Decorador dummy
    def cached(ttl=3600, key_prefix="func"):
        def decorator(func):
            return func
        return decorator


class OptimizedRAGSystem:
    """Sistema RAG otimizado com cache e lazy loading."""
    
    def __init__(self):
        """Inicializa sistema RAG otimizado."""
        self._rag_system = None
        self._embeddings_cache = {}
        self._search_cache = {}
        self.cache = get_smart_cache() if CACHE_AVAILABLE else None
        
        logger.info("🚀 Optimized RAG System inicializado")
    
    @property
    def rag_system(self) -> RAGSystem:
        """Lazy loading do RAG system."""
        if self._rag_system is None:
            logger.info("📥 Carregando RAG system (lazy)...")
            start = time.time()
            self._rag_system = get_rag_system()
            elapsed = time.time() - start
            logger.info(f"✅ RAG carregado em {elapsed:.2f}s")
        return self._rag_system
    
    def search_cached(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None,
        cache_ttl: int = 600
    ) -> List[Dict[str, Any]]:
        """
        Busca com cache automático.
        
        Args:
            query: Texto de busca
            n_results: Número de resultados
            filters: Filtros de metadata
            cache_ttl: Tempo de vida do cache (segundos)
            
        Returns:
            Lista de resultados
        """
        # Gerar chave de cache
        cache_key = f"search:{query}:{n_results}:{str(filters)}"
        
        # Tentar cache
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"💾 Search cache hit: {query[:30]}...")
                return cached_result
        
        # Executar busca
        start = time.time()
        results = self.rag_system.search(query, n_results, filters)
        elapsed = time.time() - start
        
        logger.debug(f"🔍 Search executada em {elapsed*1000:.1f}ms")
        
        # Armazenar no cache
        if self.cache and results:
            self.cache.set(cache_key, results, ttl=cache_ttl)
        
        return results
    
    def generate_context_cached(
        self,
        query: str,
        n_results: int = 3,
        max_context_length: int = 2000,
        cache_ttl: int = 300
    ) -> str:
        """
        Gera contexto com cache.
        
        Args:
            query: Pergunta do usuário
            n_results: Número de documentos
            max_context_length: Tamanho máximo
            cache_ttl: Tempo de vida do cache
            
        Returns:
            Contexto formatado
        """
        # Gerar chave de cache
        cache_key = f"context:{query}:{n_results}:{max_context_length}"
        
        # Tentar cache
        if self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"💾 Context cache hit: {query[:30]}...")
                return cached_result
        
        # Gerar contexto
        start = time.time()
        context = self.rag_system.generate_context(query, n_results, max_context_length)
        elapsed = time.time() - start
        
        logger.debug(f"📝 Contexto gerado em {elapsed*1000:.1f}ms")
        
        # Armazenar no cache
        if self.cache and context:
            self.cache.set(cache_key, context, ttl=cache_ttl)
        
        return context
    
    def add_document_optimized(
        self,
        file_path: Path,
        invalidate_cache: bool = True
    ) -> bool:
        """
        Adiciona documento e invalida cache se necessário.
        
        Args:
            file_path: Caminho do arquivo
            invalidate_cache: Se deve limpar cache
            
        Returns:
            True se sucesso
        """
        success = self.rag_system.add_document(file_path)
        
        if success and invalidate_cache and self.cache:
            # Invalidar cache de busca
            self.cache.clear("search:*")
            self.cache.clear("context:*")
            logger.info("🧹 Cache invalidado após adicionar documento")
        
        return success
    
    def batch_add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 100
    ) -> int:
        """
        Adiciona textos em lote (otimizado).
        
        Args:
            texts: Lista de textos
            metadatas: Lista de metadados
            batch_size: Tamanho do lote
            
        Returns:
            Número de textos adicionados
        """
        total_added = 0
        
        # Processar em lotes
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size] if metadatas else None
            
            # Adicionar lote
            for j, text in enumerate(batch_texts):
                meta = batch_metas[j] if batch_metas else None
                if self.rag_system.add_text(text, meta):
                    total_added += 1
            
            logger.debug(f"📦 Lote {i//batch_size + 1}: {len(batch_texts)} textos")
        
        # Invalidar cache
        if self.cache and total_added > 0:
            self.cache.clear("search:*")
            self.cache.clear("context:*")
        
        logger.info(f"✅ Adicionados {total_added} textos em lote")
        return total_added
    
    def warm_up_cache(self, common_queries: List[str]) -> None:
        """
        Aquece o cache com queries comuns.
        
        Args:
            common_queries: Lista de queries frequentes
        """
        logger.info(f"🔥 Aquecendo cache com {len(common_queries)} queries...")
        
        for query in common_queries:
            try:
                self.search_cached(query, n_results=3)
                self.generate_context_cached(query, n_results=2)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao aquecer cache: {e}")
        
        logger.info("✅ Cache aquecido")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance."""
        stats = {
            'rag_loaded': self._rag_system is not None,
            'cache_enabled': self.cache is not None,
        }
        
        if self.cache:
            cache_stats = self.cache.get_stats()
            stats.update(cache_stats)
        
        if self._rag_system:
            rag_stats = self._rag_system.get_stats()
            stats['rag_stats'] = rag_stats
        
        return stats
    
    def clear_all_caches(self) -> None:
        """Limpa todos os caches."""
        if self.cache:
            self.cache.clear()
        
        self._embeddings_cache.clear()
        self._search_cache.clear()
        
        logger.info("🧹 Todos os caches limpos")


# Instância global
_optimized_rag: Optional[OptimizedRAGSystem] = None


def get_optimized_rag() -> OptimizedRAGSystem:
    """Obtém instância global do RAG otimizado."""
    global _optimized_rag
    if _optimized_rag is None:
        _optimized_rag = OptimizedRAGSystem()
    return _optimized_rag

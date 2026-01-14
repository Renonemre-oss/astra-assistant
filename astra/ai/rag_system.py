#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA/Astra - RAG System
Sistema completo de Retrieval-Augmented Generation.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .vector_store import get_vector_store, VectorStore
from .embeddings_manager import get_embeddings_manager, EmbeddingsManager
from .document_processor import get_document_processor, DocumentProcessor

logger = logging.getLogger(__name__)


class RAGSystem:
    """Sistema RAG para busca semântica e geração aumentada."""
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embeddings_manager: Optional[EmbeddingsManager] = None,
        document_processor: Optional[DocumentProcessor] = None
    ):
        """
        Inicializa sistema RAG.
        
        Args:
            vector_store: Vector store customizado (opcional)
            embeddings_manager: Embeddings manager customizado (opcional)
            document_processor: Document processor customizado (opcional)
        """
        self.vector_store = vector_store or get_vector_store()
        self.embeddings_manager = embeddings_manager or get_embeddings_manager()
        self.document_processor = document_processor or get_document_processor()
        
        logger.info("🧠 RAG System inicializado")
    
    def add_document(self, file_path: Path) -> bool:
        """
        Adiciona documento ao sistema RAG.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se sucesso
        """
        # Processar documento
        documents = self.document_processor.process_file(file_path)
        
        if not documents:
            logger.warning(f"⚠️ Nenhum documento processado de {file_path}")
            return False
        
        # Extrair textos e metadados
        texts = [doc['text'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        # Adicionar ao vector store
        success = self.vector_store.add_documents(
            documents=texts,
            metadatas=metadatas
        )
        
        if success:
            logger.info(f"✅ Documento adicionado: {file_path.name}")
        
        return success
    
    def add_directory(self, directory: Path) -> int:
        """
        Adiciona todos os documentos de um diretório.
        
        Args:
            directory: Diretório com documentos
            
        Returns:
            Número de documentos adicionados
        """
        documents = self.document_processor.process_directory(directory)
        
        if not documents:
            logger.warning(f"⚠️ Nenhum documento encontrado em {directory}")
            return 0
        
        # Extrair textos e metadados
        texts = [doc['text'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        
        # Adicionar ao vector store
        success = self.vector_store.add_documents(
            documents=texts,
            metadatas=metadatas
        )
        
        if success:
            count = len(texts)
            logger.info(f"✅ Adicionados {count} chunks de {directory}")
            return count
        
        return 0
    
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Adiciona texto diretamente ao RAG.
        
        Args:
            text: Texto para adicionar
            metadata: Metadados opcionais
            
        Returns:
            True se sucesso
        """
        if not text.strip():
            return False
        
        metadatas = [metadata] if metadata else [{}]
        
        return self.vector_store.add_documents(
            documents=[text],
            metadatas=metadatas
        )
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca semântica por contexto relevante.
        
        Args:
            query: Pergunta ou texto de busca
            n_results: Número de resultados
            filters: Filtros de metadata
            
        Returns:
            Lista de resultados ordenados por relevância
        """
        return self.vector_store.search(
            query=query,
            n_results=n_results,
            where=filters
        )
    
    def generate_context(
        self,
        query: str,
        n_results: int = 3,
        max_context_length: int = 2000
    ) -> str:
        """
        Gera contexto para LLM baseado em busca semântica.
        
        Args:
            query: Pergunta do usuário
            n_results: Número de documentos para buscar
            max_context_length: Tamanho máximo do contexto
            
        Returns:
            Contexto formatado
        """
        # Buscar documentos relevantes
        results = self.search(query, n_results=n_results)
        
        if not results:
            return ""
        
        # Construir contexto
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(results, 1):
            doc = result['document']
            source = result['metadata'].get('source', 'unknown')
            
            # Formatar chunk
            chunk = f"[{i}] Fonte: {source}\n{doc}\n"
            
            # Verificar limite de tamanho
            if current_length + len(chunk) > max_context_length:
                break
            
            context_parts.append(chunk)
            current_length += len(chunk)
        
        context = "\n".join(context_parts)
        
        logger.info(f"📝 Contexto gerado: {len(context_parts)} documentos, {current_length} chars")
        return context
    
    def add_conversation(
        self,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Adiciona conversa ao sistema RAG.
        
        Args:
            user_message: Mensagem do usuário
            assistant_response: Resposta do assistente
            metadata: Metadados adicionais
            
        Returns:
            True se sucesso
        """
        # Combinar mensagem e resposta
        conversation = f"Usuário: {user_message}\nAssistente: {assistant_response}"
        
        # Metadados padrão
        conv_metadata = {
            'type': 'conversation',
            'user_message': user_message,
            'assistant_response': assistant_response
        }
        
        # Adicionar metadados customizados
        if metadata:
            conv_metadata.update(metadata)
        
        return self.add_text(conversation, conv_metadata)
    
    def clear(self) -> bool:
        """Limpa todos os dados do RAG."""
        return self.vector_store.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema RAG."""
        vs_stats = self.vector_store.get_stats()
        em_stats = self.embeddings_manager.get_stats()
        
        return {
            'vector_store': vs_stats,
            'embeddings': em_stats,
            'ready': vs_stats.get('available', False) and em_stats.get('available', False)
        }


# Instância global
_rag_system: Optional[RAGSystem] = None


def get_rag_system() -> RAGSystem:
    """Obtém instância global do sistema RAG."""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system



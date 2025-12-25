#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/Astra - Vector Store
Sistema de armazenamento de embeddings com ChromaDB.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store para embeddings usando ChromaDB."""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """
        Inicializa vector store.
        
        Args:
            persist_directory: Diretório para persistência
        """
        if not CHROMADB_AVAILABLE:
            logger.error("❌ ChromaDB não instalado! Use: pip install chromadb")
            self.client = None
            self.collection = None
            return
        
        # Diretório padrão
        if persist_directory is None:
            persist_directory = Path(__file__).parent.parent / 'data' / 'vector_store'
        
        persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Inicializar ChromaDB
        try:
            self.client = chromadb.PersistentClient(
                path=str(persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Criar ou obter coleção
            self.collection = self.client.get_or_create_collection(
                name="alex_memory",
                metadata={"description": "ALEX/Astra memory embeddings"}
            )
            
            logger.info(f"✅ VectorStore inicializado: {self.collection.count()} documentos")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Adiciona documentos ao vector store.
        
        Args:
            documents: Lista de textos
            metadatas: Metadados opcionais
            ids: IDs opcionais (gerados automaticamente se None)
            
        Returns:
            True se sucesso
        """
        if not self.collection:
            logger.warning("VectorStore não disponível")
            return False
        
        try:
            # Gerar IDs se não fornecidos
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            # Gerar metadados vazios se não fornecidos
            if metadatas is None:
                metadatas = [{} for _ in documents]
            
            # Adicionar à coleção
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ Adicionados {len(documents)} documentos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar documentos: {e}")
            return False
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca semântica por documentos similares.
        
        Args:
            query: Texto de busca
            n_results: Número de resultados
            where: Filtros de metadata
            
        Returns:
            Lista de resultados com documentos e scores
        """
        if not self.collection:
            logger.warning("VectorStore não disponível")
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            # Formatar resultados
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0,
                        'id': results['ids'][0][i] if results['ids'] else None
                    })
            
            logger.info(f"🔍 Busca retornou {len(formatted_results)} resultados")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
    
    def delete(self, ids: List[str]) -> bool:
        """
        Remove documentos por ID.
        
        Args:
            ids: Lista de IDs para remover
            
        Returns:
            True se sucesso
        """
        if not self.collection:
            return False
        
        try:
            self.collection.delete(ids=ids)
            logger.info(f"🗑️ Removidos {len(ids)} documentos")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao deletar: {e}")
            return False
    
    def clear(self) -> bool:
        """Limpa todos os documentos."""
        if not self.client or not self.collection:
            return False
        
        try:
            self.client.delete_collection("alex_memory")
            self.collection = self.client.create_collection("alex_memory")
            logger.info("🧹 Vector store limpo")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao limpar: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do vector store."""
        if not self.collection:
            return {
                'available': False,
                'total_documents': 0
            }
        
        return {
            'available': True,
            'total_documents': self.collection.count(),
            'collection_name': self.collection.name
        }


# Instância global
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Obtém instância global do vector store."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


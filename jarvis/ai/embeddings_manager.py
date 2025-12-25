#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - Embeddings Manager
Geração e gerenciamento de embeddings para RAG.
"""

import logging
from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """Gerencia geração de embeddings para textos."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Inicializa manager de embeddings.
        
        Args:
            model_name: Nome do modelo Sentence Transformers
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Dimensão padrão do all-MiniLM-L6-v2
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("⚠️ sentence-transformers não instalado!")
            logger.warning("Use: pip install sentence-transformers")
            return
        
        try:
            logger.info(f"📥 Carregando modelo {model_name}...")
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"✅ Modelo carregado: dim={self.embedding_dim}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")
            self.model = None
    
    def encode(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        Gera embeddings para lista de textos.
        
        Args:
            texts: Lista de textos
            
        Returns:
            Array numpy com embeddings ou None
        """
        if not self.model:
            logger.warning("Modelo não disponível")
            return None
        
        try:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            logger.debug(f"📊 Gerados {len(texts)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar embeddings: {e}")
            return None
    
    def encode_single(self, text: str) -> Optional[np.ndarray]:
        """
        Gera embedding para um único texto.
        
        Args:
            text: Texto para embedding
            
        Returns:
            Array numpy com embedding ou None
        """
        embeddings = self.encode([text])
        if embeddings is not None:
            return embeddings[0]
        return None
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcula similaridade cosseno entre dois embeddings.
        
        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding
            
        Returns:
            Score de similaridade (0-1)
        """
        try:
            # Normalizar
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Similaridade cosseno
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular similaridade: {e}")
            return 0.0
    
    def get_stats(self) -> dict:
        """Retorna informações do manager."""
        return {
            'available': self.model is not None,
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim
        }


# Instância global
_embeddings_manager: Optional[EmbeddingsManager] = None


def get_embeddings_manager() -> EmbeddingsManager:
    """Obtém instância global do embeddings manager."""
    global _embeddings_manager
    if _embeddings_manager is None:
        _embeddings_manager = EmbeddingsManager()
    return _embeddings_manager

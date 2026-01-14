#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA/Astra - RAG Memory Integration
Integração do sistema RAG com a memória do assistente.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class RAGMemoryIntegration:
    """Integra RAG com sistema de memória do assistente."""
    
    def __init__(self):
        """Inicializa integração RAG-Memory."""
        self.rag_system = None
        self.memory_system = None
        self.enabled = False
        
        # Tentar carregar RAG
        try:
            from ai import get_rag_system
            self.rag_system = get_rag_system()
            
            stats = self.rag_system.get_stats()
            if stats.get('ready', False):
                self.enabled = True
                logger.info("✅ RAG Memory Integration ativada")
            else:
                logger.warning("⚠️ RAG não está pronto - funcionando sem RAG")
                
        except ImportError as e:
            logger.warning(f"⚠️ RAG não disponível: {e}")
    
    def set_memory_system(self, memory_system):
        """
        Conecta ao sistema de memória existente.
        
        Args:
            memory_system: Instância do MemorySystem
        """
        self.memory_system = memory_system
        logger.info("🔗 Sistema de memória conectado ao RAG")
    
    def save_conversation(
        self,
        user_message: str,
        assistant_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Salva conversa no RAG para busca semântica futura.
        
        Args:
            user_message: Mensagem do usuário
            assistant_response: Resposta do assistente
            context: Contexto adicional da conversa
            
        Returns:
            True se salvou com sucesso
        """
        if not self.enabled or not self.rag_system:
            return False
        
        try:
            # Preparar metadados
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'type': 'conversation',
                'has_context': bool(context)
            }
            
            # Adicionar contexto se disponível
            if context:
                if 'emotion' in context:
                    metadata['emotion'] = context['emotion']
                if 'topic' in context:
                    metadata['topic'] = context['topic']
                if 'user_name' in context:
                    metadata['user_name'] = context['user_name']
            
            # Salvar no RAG
            success = self.rag_system.add_conversation(
                user_message=user_message,
                assistant_response=assistant_response,
                metadata=metadata
            )
            
            if success:
                logger.debug(f"💾 Conversa salva no RAG")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar conversa no RAG: {e}")
            return False
    
    def retrieve_context(
        self,
        query: str,
        n_results: int = 3,
        filters: Optional[Dict] = None
    ) -> str:
        """
        Recupera contexto relevante do RAG.
        
        Args:
            query: Mensagem do usuário
            n_results: Número de conversas passadas para buscar
            filters: Filtros opcionais (ex: user_name, emotion)
            
        Returns:
            Contexto formatado ou string vazia
        """
        if not self.enabled or not self.rag_system:
            return ""
        
        try:
            # Buscar contexto relevante
            context = self.rag_system.generate_context(
                query=query,
                n_results=n_results,
                max_context_length=1500
            )
            
            if context:
                logger.debug(f"🔍 Contexto RAG recuperado: {len(context)} chars")
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar contexto RAG: {e}")
            return ""
    
    def search_memories(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca memórias semanticamente relacionadas.
        
        Args:
            query: Texto de busca
            n_results: Número de resultados
            filters: Filtros de metadata
            
        Returns:
            Lista de memórias encontradas
        """
        if not self.enabled or not self.rag_system:
            return []
        
        try:
            results = self.rag_system.search(
                query=query,
                n_results=n_results,
                filters=filters
            )
            
            logger.debug(f"🔍 Encontradas {len(results)} memórias relacionadas")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar memórias: {e}")
            return []
    
    def add_knowledge(
        self,
        text: str,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Adiciona conhecimento ao RAG.
        
        Args:
            text: Texto do conhecimento
            category: Categoria do conhecimento
            metadata: Metadados adicionais
            
        Returns:
            True se adicionou com sucesso
        """
        if not self.enabled or not self.rag_system:
            return False
        
        try:
            meta = metadata or {}
            meta['category'] = category
            meta['type'] = 'knowledge'
            meta['timestamp'] = datetime.now().isoformat()
            
            success = self.rag_system.add_text(text, metadata=meta)
            
            if success:
                logger.info(f"📚 Conhecimento adicionado: {category}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar conhecimento: {e}")
            return False
    
    def get_conversation_summary(self, n_conversations: int = 10) -> str:
        """
        Gera resumo das últimas conversas usando RAG.
        
        Args:
            n_conversations: Número de conversas para resumir
            
        Returns:
            Resumo textual
        """
        if not self.enabled or not self.rag_system:
            return "Sistema de memória RAG não disponível."
        
        try:
            # Buscar conversas recentes
            results = self.rag_system.search(
                query="conversas recentes",
                n_results=n_conversations,
                filters={'type': 'conversation'}
            )
            
            if not results:
                return "Nenhuma conversa anterior encontrada."
            
            # Construir resumo
            summary_parts = ["📝 Resumo das últimas conversas:\n"]
            
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                timestamp = metadata.get('timestamp', 'desconhecido')
                
                # Extrair data/hora
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%d/%m %H:%M")
                except:
                    time_str = "?"
                
                doc = result['document'][:150]
                summary_parts.append(f"[{time_str}] {doc}...")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo: {e}")
            return "Erro ao gerar resumo."
    
    def clear_old_memories(self, days: int = 30) -> int:
        """
        Limpa memórias antigas do RAG.
        
        Args:
            days: Número de dias para manter
            
        Returns:
            Número de memórias removidas
        """
        # TODO: Implementar limpeza baseada em timestamp
        logger.info(f"⚠️ Limpeza de memórias ainda não implementada")
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema RAG-Memory."""
        if not self.enabled or not self.rag_system:
            return {
                'enabled': False,
                'reason': 'RAG system not available'
            }
        
        rag_stats = self.rag_system.get_stats()
        
        return {
            'enabled': True,
            'rag_ready': rag_stats.get('ready', False),
            'total_documents': rag_stats.get('vector_store', {}).get('total_documents', 0),
            'embedding_model': rag_stats.get('embeddings', {}).get('model_name', 'unknown'),
            'memory_system_connected': self.memory_system is not None
        }


# Instância global
_rag_memory_integration: Optional[RAGMemoryIntegration] = None


def get_rag_memory_integration() -> RAGMemoryIntegration:
    """Obtém instância global da integração RAG-Memory."""
    global _rag_memory_integration
    if _rag_memory_integration is None:
        _rag_memory_integration = RAGMemoryIntegration()
    return _rag_memory_integration



#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Jarvis AI Assistant - Base AI Provider
Classe base abstrata para todos os provedores de IA.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Status do provedor de IA."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class AIMessage:
    """Representa uma mensagem na conversa."""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResponse:
    """Resposta padronizada de um provedor de IA."""
    content: str
    provider: str
    model: str
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Verifica se a resposta foi bem-sucedida."""
        return self.error is None and self.content is not None


class AIProviderBase(ABC):
    """
    Classe base abstrata para todos os provedores de IA.
    
    Todos os provedores devem herdar desta classe e implementar os métodos abstratos.
    Isso garante uma interface consistente independente do provider usado.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o provedor de IA.
        
        Args:
            config: Dicionário com configurações do provedor
        """
        self.config = config
        self.name = self.__class__.__name__.replace("Provider", "").lower()
        self.status = ProviderStatus.UNAVAILABLE
        self.last_error: Optional[str] = None
        self._conversation_history: List[AIMessage] = []
        
        logger.info(f"Inicializando provedor: {self.name}")
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> AIResponse:
        """
        Gera uma resposta baseada no prompt fornecido.
        
        Args:
            prompt: O prompt do usuário
            system_prompt: Prompt de sistema (contexto/instruções)
            temperature: Controle de aleatoriedade (0.0 - 1.0)
            max_tokens: Número máximo de tokens na resposta
            stop_sequences: Sequências que param a geração
            **kwargs: Parâmetros específicos do provedor
            
        Returns:
            AIResponse: Resposta padronizada do modelo
        """
        pass
    
    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Gera uma resposta em modo streaming.
        
        Args:
            prompt: O prompt do usuário
            system_prompt: Prompt de sistema
            temperature: Controle de aleatoriedade
            max_tokens: Número máximo de tokens
            **kwargs: Parâmetros específicos do provedor
            
        Yields:
            str: Chunks da resposta conforme são gerados
        """
        pass
    
    @abstractmethod
    def check_availability(self) -> bool:
        """
        Verifica se o provedor está disponível e funcionando.
        
        Returns:
            bool: True se disponível, False caso contrário
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        Lista modelos disponíveis neste provedor.
        
        Returns:
            List[str]: Lista de nomes de modelos
        """
        pass
    
    def get_status(self) -> ProviderStatus:
        """
        Retorna o status atual do provedor.
        
        Returns:
            ProviderStatus: Status do provedor
        """
        return self.status
    
    def add_to_history(self, role: str, content: str, metadata: Dict = None):
        """
        Adiciona uma mensagem ao histórico da conversa.
        
        Args:
            role: Papel da mensagem ('user', 'assistant', 'system')
            content: Conteúdo da mensagem
            metadata: Metadados adicionais
        """
        message = AIMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self._conversation_history.append(message)
    
    def get_history(self, limit: Optional[int] = None) -> List[AIMessage]:
        """
        Retorna o histórico da conversa.
        
        Args:
            limit: Número máximo de mensagens a retornar
            
        Returns:
            List[AIMessage]: Lista de mensagens
        """
        if limit:
            return self._conversation_history[-limit:]
        return self._conversation_history.copy()
    
    def clear_history(self):
        """Limpa o histórico da conversa."""
        self._conversation_history.clear()
        logger.info(f"Histórico limpo para provedor: {self.name}")
    
    def set_status(self, status: ProviderStatus, error: Optional[str] = None):
        """
        Define o status do provedor.
        
        Args:
            status: Novo status
            error: Mensagem de erro (opcional)
        """
        self.status = status
        self.last_error = error
        
        if error:
            logger.error(f"Provedor {self.name}: {error}")
        else:
            logger.info(f"Provedor {self.name}: status = {status.value}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor de configuração.
        
        Args:
            key: Chave da configuração
            default: Valor padrão se não encontrada
            
        Returns:
            Any: Valor da configuração
        """
        return self.config.get(key, default)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} status={self.status.value}>"

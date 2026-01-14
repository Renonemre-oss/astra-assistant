#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra AI Assistant - Base Skill
Classe base abstrata para todas as skills do Astra.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SkillPriority(Enum):
    """Prioridade de execução da skill."""
    CRITICAL = 100    # Skills críticas executam primeiro
    HIGH = 75
    NORMAL = 50
    LOW = 25
    MINIMAL = 1


class SkillStatus(Enum):
    """Status da skill."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class SkillMetadata:
    """Metadados de uma skill."""
    name: str
    version: str
    description: str
    author: str = "Astra Team"
    dependencies: List[str] = field(default_factory=list)
    requires_api_keys: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    priority: SkillPriority = SkillPriority.NORMAL
    enabled_by_default: bool = True


@dataclass
class SkillResponse:
    """Resposta de uma skill."""
    success: bool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    @staticmethod
    def success_response(content: str, metadata: Dict = None) -> 'SkillResponse':
        """Cria uma resposta de sucesso."""
        return SkillResponse(
            success=True,
            content=content,
            metadata=metadata or {}
        )
    
    @staticmethod
    def error_response(error: str, metadata: Dict = None) -> 'SkillResponse':
        """Cria uma resposta de erro."""
        return SkillResponse(
            success=False,
            content="",
            error=error,
            metadata=metadata or {}
        )


class BaseSkill(ABC):
    """
    Classe base abstrata para todas as skills do Astra.
    
    Uma skill é uma capacidade específica do assistente, como:
    - Obter previsão do tempo
    - Buscar notícias
    - Gerenciar memória
    - Controlar dispositivos IoT
    - Etc.
    
    Todas as skills devem herdar desta classe e implementar os métodos abstratos.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa a skill.
        
        Args:
            config: Configuração específica da skill
        """
        self.config = config or {}
        self.status = SkillStatus.INACTIVE
        self.metadata = self.get_metadata()
        self._initialized = False
        self.last_error: Optional[str] = None
        
        logger.info(f"Skill criada: {self.metadata.name}")
    
    @abstractmethod
    def get_metadata(self) -> SkillMetadata:
        """
        Retorna metadados da skill.
        
        Returns:
            SkillMetadata: Informações sobre a skill
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Inicializa a skill (chamado uma vez ao carregar).
        
        Use este método para:
        - Verificar dependências
        - Carregar dados necessários
        - Validar configurações
        - Conectar a serviços externos
        
        Returns:
            bool: True se inicializado com sucesso
        """
        pass
    
    @abstractmethod
    def can_handle(self, query: str, context: Dict[str, Any]) -> bool:
        """
        Verifica se a skill pode lidar com a query do usuário.
        
        Args:
            query: Query/comando do usuário
            context: Contexto da conversa
            
        Returns:
            bool: True se a skill pode processar esta query
        """
        pass
    
    @abstractmethod
    def execute(self, query: str, context: Dict[str, Any]) -> SkillResponse:
        """
        Executa a skill para processar a query.
        
        Args:
            query: Query/comando do usuário
            context: Contexto da conversa
            
        Returns:
            SkillResponse: Resposta da skill
        """
        pass
    
    def activate(self) -> bool:
        """
        Ativa a skill.
        
        Returns:
            bool: True se ativada com sucesso
        """
        try:
            if not self._initialized:
                if not self.initialize():
                    self.set_status(SkillStatus.ERROR, "Falha ao inicializar")
                    return False
                self._initialized = True
            
            self.status = SkillStatus.ACTIVE
            logger.info(f"Skill ativada: {self.metadata.name}")
            return True
        
        except Exception as e:
            error_msg = f"Erro ao ativar skill: {e}"
            logger.error(error_msg)
            self.set_status(SkillStatus.ERROR, error_msg)
            return False
    
    def deactivate(self) -> bool:
        """
        Desativa a skill.
        
        Returns:
            bool: True se desativada com sucesso
        """
        try:
            self.status = SkillStatus.INACTIVE
            self.cleanup()
            logger.info(f"Skill desativada: {self.metadata.name}")
            return True
        
        except Exception as e:
            error_msg = f"Erro ao desativar skill: {e}"
            logger.error(error_msg)
            return False
    
    def cleanup(self):
        """
        Limpa recursos da skill (chamado ao desativar).
        
        Use este método para:
        - Fechar conexões
        - Salvar dados
        - Liberar recursos
        """
        pass
    
    def is_active(self) -> bool:
        """Verifica se a skill está ativa."""
        return self.status == SkillStatus.ACTIVE
    
    def get_status(self) -> SkillStatus:
        """Retorna o status atual da skill."""
        return self.status
    
    def set_status(self, status: SkillStatus, error: Optional[str] = None):
        """
        Define o status da skill.
        
        Args:
            status: Novo status
            error: Mensagem de erro (opcional)
        """
        self.status = status
        self.last_error = error
        
        if error:
            logger.error(f"Skill {self.metadata.name}: {error}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor de configuração.
        
        Args:
            key: Chave da configuração
            default: Valor padrão
            
        Returns:
            Any: Valor da configuração
        """
        return self.config.get(key, default)
    
    def validate_dependencies(self) -> bool:
        """
        Valida se todas as dependências estão disponíveis.
        
        Returns:
            bool: True se todas as dependências estão OK
        """
        for dependency in self.metadata.dependencies:
            try:
                __import__(dependency)
            except ImportError:
                error_msg = f"Dependência ausente: {dependency}"
                logger.error(error_msg)
                self.set_status(SkillStatus.ERROR, error_msg)
                return False
        return True
    
    def validate_api_keys(self) -> bool:
        """
        Valida se todas as API keys necessárias estão configuradas.
        
        Returns:
            bool: True se todas as keys estão configuradas
        """
        for key_name in self.metadata.requires_api_keys:
            if not self.get_config(key_name):
                error_msg = f"API key ausente: {key_name}"
                logger.error(error_msg)
                self.set_status(SkillStatus.ERROR, error_msg)
                return False
        return True
    
    def get_help(self) -> str:
        """
        Retorna texto de ajuda sobre como usar a skill.
        
        Returns:
            str: Texto de ajuda
        """
        return f"""
Skill: {self.metadata.name} v{self.metadata.version}
{self.metadata.description}

Palavras-chave: {', '.join(self.metadata.keywords)}
Status: {self.status.value}
        """.strip()
    
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.metadata.name}' "
            f"status={self.status.value}>"
        )


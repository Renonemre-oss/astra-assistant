#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Sistema de Exceções Customizadas
Hierarquia completa de exceções para tratamento de erros específicos do sistema.
"""

from typing import Optional, Any, Dict


# ==========================
# BASE EXCEPTION
# ==========================
class ASTRAException(Exception):
    """Exceção base para todo o sistema ASTRA."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# ==========================
# CONFIGURATION EXCEPTIONS
# ==========================
class ConfigurationError(ASTRAException):
    """Erro de configuração do sistema."""
    pass


class MissingConfigError(ConfigurationError):
    """Configuração necessária não encontrada."""
    pass


class InvalidConfigError(ConfigurationError):
    """Configuração inválida ou malformada."""
    pass


# ==========================
# DATABASE EXCEPTIONS
# ==========================
class DatabaseError(ASTRAException):
    """Erro relacionado à base de dados."""
    pass


class DatabaseConnectionError(DatabaseError):
    """Erro ao conectar à base de dados."""
    pass


class DatabaseQueryError(DatabaseError):
    """Erro ao executar query na base de dados."""
    pass


class DatabaseIntegrityError(DatabaseError):
    """Violação de integridade na base de dados."""
    pass


class DatabaseNotAvailableError(DatabaseError):
    """Base de dados não disponível."""
    pass


# ==========================
# API EXCEPTIONS
# ==========================
class APIError(ASTRAException):
    """Erro relacionado a APIs externas."""
    pass


class APIConnectionError(APIError):
    """Erro de conexão com API externa."""
    pass


class APITimeoutError(APIError):
    """Timeout ao chamar API externa."""
    pass


class APIRateLimitError(APIError):
    """Rate limit excedido em API externa."""
    pass


class APIAuthenticationError(APIError):
    """Erro de autenticação em API externa."""
    pass


class APIResponseError(APIError):
    """Resposta inválida ou inesperada de API externa."""
    pass


# ==========================
# OLLAMA EXCEPTIONS
# ==========================
class OllamaError(ASTRAException):
    """Erro relacionado ao Ollama."""
    pass


class OllamaConnectionError(OllamaError):
    """Erro ao conectar ao Ollama."""
    pass


class OllamaModelNotFoundError(OllamaError):
    """Modelo Ollama não encontrado."""
    pass


class OllamaTimeoutError(OllamaError):
    """Timeout ao obter resposta do Ollama."""
    pass


class OllamaResponseError(OllamaError):
    """Resposta inválida do Ollama."""
    pass


# ==========================
# SPEECH/AUDIO EXCEPTIONS
# ==========================
class SpeechError(ASTRAException):
    """Erro relacionado a speech (TTS/STT)."""
    pass


class TTSError(SpeechError):
    """Erro no sistema Text-to-Speech."""
    pass


class TTSEngineNotAvailableError(TTSError):
    """Engine TTS não disponível."""
    pass


class STTError(SpeechError):
    """Erro no sistema Speech-to-Text."""
    pass


class AudioError(ASTRAException):
    """Erro relacionado a áudio."""
    pass


class AudioDeviceError(AudioError):
    """Erro de dispositivo de áudio."""
    pass


class AudioRecordingError(AudioError):
    """Erro durante gravação de áudio."""
    pass


class AudioPlaybackError(AudioError):
    """Erro durante reprodução de áudio."""
    pass


# ==========================
# PERSONALITY EXCEPTIONS
# ==========================
class PersonalityError(ASTRAException):
    """Erro no sistema de personalidade."""
    pass


class InvalidPersonalityModeError(PersonalityError):
    """Modo de personalidade inválido."""
    pass


class PersonalityDataError(PersonalityError):
    """Erro nos dados de personalidade."""
    pass


# ==========================
# MEMORY EXCEPTIONS
# ==========================
class MemoryError(ASTRAException):
    """Erro no sistema de memória."""
    pass


class MemoryStorageError(MemoryError):
    """Erro ao armazenar memória."""
    pass


class MemoryRetrievalError(MemoryError):
    """Erro ao recuperar memória."""
    pass


class MemoryNotFoundError(MemoryError):
    """Memória não encontrada."""
    pass


# ==========================
# USER EXCEPTIONS
# ==========================
class UserError(ASTRAException):
    """Erro relacionado a usuários."""
    pass


class UserNotFoundError(UserError):
    """Usuário não encontrado."""
    pass


class UserIdentificationError(UserError):
    """Erro ao identificar usuário."""
    pass


class InvalidUserDataError(UserError):
    """Dados de usuário inválidos."""
    pass


# ==========================
# PLUGIN EXCEPTIONS
# ==========================
class PluginError(ASTRAException):
    """Erro relacionado a plugins."""
    pass


class PluginLoadError(PluginError):
    """Erro ao carregar plugin."""
    pass


class PluginNotFoundError(PluginError):
    """Plugin não encontrado."""
    pass


class PluginVersionError(PluginError):
    """Versão de plugin incompatível."""
    pass


class PluginExecutionError(PluginError):
    """Erro durante execução de plugin."""
    pass


# ==========================
# VALIDATION EXCEPTIONS
# ==========================
class ValidationError(ASTRAException):
    """Erro de validação de dados."""
    pass


class InvalidInputError(ValidationError):
    """Input inválido do usuário."""
    pass


class DataTypeError(ValidationError):
    """Tipo de dado incorreto."""
    pass


class ValueRangeError(ValidationError):
    """Valor fora do range permitido."""
    pass


# ==========================
# FILE EXCEPTIONS
# ==========================
class FileError(ASTRAException):
    """Erro relacionado a arquivos."""
    pass


class FileNotFoundError(FileError):
    """Arquivo não encontrado."""
    pass


class FileReadError(FileError):
    """Erro ao ler arquivo."""
    pass


class FileWriteError(FileError):
    """Erro ao escrever arquivo."""
    pass


class FilePermissionError(FileError):
    """Permissão negada para arquivo."""
    pass


# ==========================
# NETWORK EXCEPTIONS
# ==========================
class NetworkError(ASTRAException):
    """Erro relacionado a rede."""
    pass


class ConnectionError(NetworkError):
    """Erro de conexão de rede."""
    pass


class TimeoutError(NetworkError):
    """Timeout de rede."""
    pass


# ==========================
# CACHE EXCEPTIONS
# ==========================
class CacheError(ASTRAException):
    """Erro relacionado ao sistema de cache."""
    pass


class CacheInvalidationError(CacheError):
    """Erro ao invalidar cache."""
    pass


class CacheStorageError(CacheError):
    """Erro ao armazenar no cache."""
    pass


# ==========================
# RESOURCE EXCEPTIONS
# ==========================
class ResourceError(ASTRAException):
    """Erro relacionado a recursos do sistema."""
    pass


class ResourceNotAvailableError(ResourceError):
    """Recurso não disponível."""
    pass


class ResourceExhaustedError(ResourceError):
    """Recursos do sistema esgotados (memória, CPU, etc)."""
    pass


class ResourceLockError(ResourceError):
    """Erro ao obter lock de recurso."""
    pass


# ==========================
# CONTEXTUAL EXCEPTIONS
# ==========================
class ContextualError(ASTRAException):
    """Erro no sistema de análise contextual."""
    pass


class ContextAnalysisError(ContextualError):
    """Erro ao analisar contexto."""
    pass


# ==========================
# COMPANION EXCEPTIONS
# ==========================
class CompanionError(ASTRAException):
    """Erro no sistema companion."""
    pass


class CompanionModeError(CompanionError):
    """Erro ao definir modo companion."""
    pass


# ==========================
# HELPER FUNCTIONS
# ==========================
def get_exception_hierarchy() -> Dict[str, Any]:
    """
    Retorna a hierarquia completa de exceções do sistema.
    
    Returns:
        Dict com a estrutura hierárquica das exceções
    """
    return {
        'ASTRAException': {
            'ConfigurationError': ['MissingConfigError', 'InvalidConfigError'],
            'DatabaseError': [
                'DatabaseConnectionError',
                'DatabaseQueryError',
                'DatabaseIntegrityError',
                'DatabaseNotAvailableError'
            ],
            'APIError': [
                'APIConnectionError',
                'APITimeoutError',
                'APIRateLimitError',
                'APIAuthenticationError',
                'APIResponseError'
            ],
            'OllamaError': [
                'OllamaConnectionError',
                'OllamaModelNotFoundError',
                'OllamaTimeoutError',
                'OllamaResponseError'
            ],
            'SpeechError': [
                'TTSError',
                'TTSEngineNotAvailableError',
                'STTError'
            ],
            'AudioError': [
                'AudioDeviceError',
                'AudioRecordingError',
                'AudioPlaybackError'
            ],
            'PersonalityError': [
                'InvalidPersonalityModeError',
                'PersonalityDataError'
            ],
            'MemoryError': [
                'MemoryStorageError',
                'MemoryRetrievalError',
                'MemoryNotFoundError'
            ],
            'UserError': [
                'UserNotFoundError',
                'UserIdentificationError',
                'InvalidUserDataError'
            ],
            'PluginError': [
                'PluginLoadError',
                'PluginNotFoundError',
                'PluginVersionError',
                'PluginExecutionError'
            ],
            'ValidationError': [
                'InvalidInputError',
                'DataTypeError',
                'ValueRangeError'
            ],
            'FileError': [
                'FileNotFoundError',
                'FileReadError',
                'FileWriteError',
                'FilePermissionError'
            ],
            'NetworkError': ['ConnectionError', 'TimeoutError'],
            'CacheError': ['CacheInvalidationError', 'CacheStorageError'],
            'ResourceError': [
                'ResourceNotAvailableError',
                'ResourceExhaustedError',
                'ResourceLockError'
            ],
            'ContextualError': ['ContextAnalysisError'],
            'CompanionError': ['CompanionModeError']
        }
    }


def is_critical_error(exception: Exception) -> bool:
    """
    Verifica se uma exceção é crítica e requer atenção imediata.
    
    Args:
        exception: Exceção a verificar
        
    Returns:
        True se for crítica, False caso contrário
    """
    critical_exceptions = (
        DatabaseConnectionError,
        ResourceExhaustedError,
        ConfigurationError,
        ResourceNotAvailableError
    )
    return isinstance(exception, critical_exceptions)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Factories para Testes
Fornece funções de criação de mocks e objetos de teste comuns
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Callable
from unittest.mock import Mock, MagicMock, patch

# Importar o sistema de configuração
try:
    from .test_config import get_mock_config, get_test_setting
except ImportError:
    from test_config import get_mock_config, get_test_setting


class MockFactory:
    """Factory para criação de objetos Mock para testes."""
    
    @staticmethod
    def create_process_mock() -> Mock:
        """
        Cria mock de processo para testes do performance_manager.
        
        Returns:
            Mock configurado para simular um processo
        """
        config = get_mock_config("performance_manager")
        
        mock_process = Mock()
        mock_process.cpu_percent.return_value = config.get("cpu_percent", 25.0)
        mock_process.memory_percent.return_value = config.get("memory_percent", 45.0)
        
        # Configurar memory_info com rss
        memory_rss = config.get("memory_rss", 100 * 1024 * 1024)  # Padrão: 100MB
        mock_memory_info = Mock()
        mock_memory_info.rss = memory_rss
        mock_process.memory_info.return_value = mock_memory_info
        
        # Outros atributos
        mock_process.num_threads.return_value = config.get("num_threads", 5)
        
        return mock_process
    
    @staticmethod
    def create_psutil_mock() -> Mock:
        """
        Cria mock de psutil para testes.
        
        Returns:
            Mock configurado para simular o módulo psutil
        """
        mock_psutil = Mock()
        mock_psutil.Process.return_value = MockFactory.create_process_mock()
        return mock_psutil
    
    @staticmethod
    def create_audio_dependencies_mock() -> Dict[str, bool]:
        """
        Cria mock para DEPENDENCIES no audio_manager.
        
        Returns:
            Dicionário de dependências simulado
        """
        config = get_mock_config("audio_manager")
        dependencies = config.get("dependencies", {})
        
        # Se não tiver configurações específicas, usar valores padrão
        if not dependencies:
            dependencies = {"TTS": False, "simpleaudio": False}
            
        return dependencies
    
    @staticmethod
    def create_config_mock(config_values: Dict[str, Any] = None) -> Mock:
        """
        Cria mock do CONFIG para testes.
        
        Args:
            config_values: Valores personalizados para o mock
            
        Returns:
            Mock configurado para simular CONFIG
        """
        mock_config = MagicMock()
        
        # Implementar __getitem__ para simular comportamento de dicionário
        if config_values:
            mock_config.__getitem__.side_effect = lambda key: config_values.get(key)
        
        return mock_config
    
    @staticmethod
    def patch_dependency(module_path: str, attr_name: Optional[str] = None, 
                        return_value: Any = None) -> Callable:
        """
        Cria um patch para dependência externa.
        
        Args:
            module_path: Caminho do módulo a ser mockado
            attr_name: Nome do atributo a ser mockado (se for None, mock todo o módulo)
            return_value: Valor de retorno para o mock
            
        Returns:
            Decorator de patch configurado
        """
        target = f"{module_path}.{attr_name}" if attr_name else module_path
        
        # Criar patch com o comportamento desejado
        if return_value is not None:
            return patch(target, return_value=return_value)
        else:
            return patch(target)


class FileFactory:
    """Factory para criação de arquivos de teste."""
    
    @staticmethod
    def create_temp_dir() -> Path:
        """
        Cria diretório temporário para testes.
        
        Returns:
            Path para o diretório criado
        """
        return Path(tempfile.mkdtemp())
    
    @staticmethod
    def create_temp_file(dir_path: Path, filename: str, content: str = "") -> Path:
        """
        Cria arquivo temporário com conteúdo específico.
        
        Args:
            dir_path: Diretório onde criar o arquivo
            filename: Nome do arquivo
            content: Conteúdo inicial do arquivo
            
        Returns:
            Path para o arquivo criado
        """
        file_path = dir_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    @staticmethod
    def create_json_file(dir_path: Path, filename: str, data: Dict[str, Any]) -> Path:
        """
        Cria arquivo JSON temporário.
        
        Args:
            dir_path: Diretório onde criar o arquivo
            filename: Nome do arquivo
            data: Dados a serem convertidos em JSON
            
        Returns:
            Path para o arquivo criado
        """
        import json
        content = json.dumps(data, indent=2, ensure_ascii=False)
        return FileFactory.create_temp_file(dir_path, filename, content)
    
    @staticmethod
    def cleanup_dir(dir_path: Path) -> None:
        """
        Remove diretório temporário e seu conteúdo.
        
        Args:
            dir_path: Diretório a ser removido
        """
        import shutil
        if dir_path.exists() and get_test_setting("temp_cleanup", True):
            shutil.rmtree(dir_path, ignore_errors=True)


class TestDataBuilder:
    """Builder para criação de dados de teste."""
    
    @staticmethod
    def build_validation_test_data() -> Dict[str, Any]:
        """
        Cria dados para testes de validação.
        
        Returns:
            Dados de teste para validadores
        """
        config = get_mock_config("validation_tests")
        
        return {
            "test_string": config.get("test_string", "test"),
            "test_field": config.get("test_field", "test_field"),
            "test_value": config.get("test_value", "test_value"),
            "min_length": config.get("min_length", 1),
            "max_length": config.get("max_length", 10),
            "numeric_min": config.get("numeric_min", 0),
            "numeric_max": config.get("numeric_max", 10),
            "numeric_test": config.get("numeric_test", 5),
            "numeric_fail": config.get("numeric_fail", 15)
        }
    
    @staticmethod
    def build_performance_test_params() -> Dict[str, Any]:
        """
        Cria parâmetros para testes de performance.
        
        Returns:
            Parâmetros para testes de performance
        """
        return {
            "max_workers": get_mock_config("performance_manager").get("max_workers", 2),
            "cache_size": get_mock_config("performance_manager").get("cache_size", 100),
            "cache_ttl": get_mock_config("performance_manager").get("cache_ttl", 1)
        }
    
    @staticmethod
    def build_mock_file_data(file_type: str) -> Dict[str, Any]:
        """
        Cria dados para arquivos mock.
        
        Args:
            file_type: Tipo de arquivo a criar dados
            
        Returns:
            Dados mock para o tipo especificado
        """
        if file_type == "personal_facts":
            return {"name": "Test User", "likes": ["testing", "python"], "dislikes": []}
        elif file_type == "config":
            return {
                "ollama_model": "test_model",
                "conversation_history_size": 3,
                "max_retries": 3
            }
        else:
            return {}


# Classes de mock comuns para uso nos testes
class MockLogger:
    """Mock simples para logger."""
    
    def __init__(self):
        self.logs = {
            "debug": [],
            "info": [],
            "warning": [],
            "error": [],
            "critical": []
        }
        self.handlers = []
        self.level = 0  # Simular nível de logging
        self.disabled = False
    
    def debug(self, message, *args, **kwargs):
        self.logs["debug"].append(message)
    
    def info(self, message, *args, **kwargs):
        self.logs["info"].append(message)
    
    def warning(self, message, *args, **kwargs):
        self.logs["warning"].append(message)
    
    def error(self, message, *args, **kwargs):
        self.logs["error"].append(message)
    
    def critical(self, message, *args, **kwargs):
        self.logs["critical"].append(message)
    
    def addHandler(self, handler):
        """Adiciona handler (compatibilidade com bibliotecas externas)."""
        self.handlers.append(handler)
    
    def removeHandler(self, handler):
        """Remove handler (compatibilidade com bibliotecas externas)."""
        if handler in self.handlers:
            self.handlers.remove(handler)
    
    def setLevel(self, level):
        """Define nível de logging (compatibilidade com bibliotecas externas)."""
        self.level = level
    
    def getLevel(self):
        """Obtém nível de logging (compatibilidade com bibliotecas externas)."""
        return self.level
    
    def isEnabledFor(self, level):
        """Verifica se logging está habilitado para o nível (compatibilidade)."""
        return not self.disabled and level >= self.level
    
    def reset(self):
        """Limpa todos os logs."""
        for key in self.logs:
            self.logs[key] = []
    
    def get_log_count(self, level=None):
        """Obtém contagem de logs de um nível específico ou total."""
        if level:
            return len(self.logs.get(level, []))
        return sum(len(logs) for logs in self.logs.values())


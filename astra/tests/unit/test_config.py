#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Sistema de Configuração para Testes
Gerencia configurações dinâmicas para testes do framework
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum

# Tipos de configuração
class ConfigType(Enum):
    """Tipos de configuração disponíveis."""
    MOCK = "mock_settings"
    FRAMEWORK = "test_framework"
    SUITES = "test_suites"
    FILES = "file_patterns"

@dataclass
class TestSettings:
    """Classe para configurações de testes."""
    logging_level: str = "INFO"
    temp_cleanup: bool = True
    skip_unavailable_modules: bool = True
    timeout_seconds: int = 30
    performance_thresholds: Dict[str, float] = field(default_factory=dict)

@dataclass
class MockConfig:
    """Configuração para mocks nos testes."""
    performance_manager: Dict[str, Any] = field(default_factory=dict)
    audio_manager: Dict[str, Any] = field(default_factory=dict)
    validation_tests: Dict[str, Any] = field(default_factory=dict)

class TestConfigManager:
    """Gerenciador centralizado de configurações para testes."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file: Caminho para arquivo de configuração personalizado
        """
        self.project_root = Path(__file__).parent.parent
        self.config_file = config_file or (self.project_root / "config" / "test_settings.json")
        self._config_cache: Optional[Dict[str, Any]] = None
        self._logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Configura logger para o gerenciador."""
        logger = logging.getLogger(f"{__name__}.TestConfigManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Carrega configurações do arquivo JSON.
        
        Args:
            force_reload: Força recarregamento mesmo se já em cache
            
        Returns:
            Dicionário com todas as configurações
        """
        if self._config_cache is not None and not force_reload:
            return self._config_cache
            
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
                self._logger.info(f"Configurações carregadas de {self.config_file}")
            else:
                self._logger.warning(f"Arquivo de configuração não encontrado: {self.config_file}")
                self._config_cache = self._get_default_config()
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self._logger.error(f"Erro ao carregar configurações: {e}")
            self._config_cache = self._get_default_config()
            
        return self._config_cache

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão caso não exista arquivo."""
        return {
            "test_framework": {
                "logging_level": "INFO",
                "temp_cleanup": True,
                "skip_unavailable_modules": True,
                "timeout_seconds": 30,
                "performance_thresholds": {
                    "write_time_max": 1.0,
                    "read_time_max": 1.0,
                    "memory_usage_max": 100
                }
            },
            "mock_settings": {
                "performance_manager": {
                    "cpu_percent": 25.0,
                    "memory_percent": 45.0,
                    "memory_rss": 104857600,
                    "num_threads": 5,
                    "max_workers": 2,
                    "cache_size": 100,
                    "cache_ttl": 1
                },
                "audio_manager": {
                    "tts_loaded": False,
                    "dependencies": {"TTS": False, "simpleaudio": False}
                },
                "validation_tests": {
                    "test_string": "test",
                    "test_field": "test_field",
                    "test_value": "test_value",
                    "min_length": 1,
                    "max_length": 10,
                    "numeric_min": 0,
                    "numeric_max": 10,
                    "numeric_test": 5,
                    "numeric_fail": 15
                }
            }
        }

    def get_config(self, section: Union[str, ConfigType], key: Optional[str] = None) -> Any:
        """
        Obtém configuração específica.
        
        Args:
            section: Seção da configuração
            key: Chave específica dentro da seção (opcional)
            
        Returns:
            Valor da configuração solicitada
        """
        config = self.load_config()
        
        section_name = section.value if isinstance(section, ConfigType) else section
        
        if section_name not in config:
            self._logger.warning(f"Seção '{section_name}' não encontrada")
            return None
            
        section_data = config[section_name]
        
        if key is None:
            return section_data
            
        return section_data.get(key, None)

    def get_mock_config(self, module: str) -> Dict[str, Any]:
        """
        Obtém configuração específica para mocks.
        
        Args:
            module: Nome do módulo para mock
            
        Returns:
            Configuração do mock
        """
        return self.get_config(ConfigType.MOCK, module) or {}

    def get_test_setting(self, key: str, default: Any = None) -> Any:
        """
        Obtém configuração específica do framework de testes.
        
        Args:
            key: Chave da configuração
            default: Valor padrão se não encontrada
            
        Returns:
            Valor da configuração
        """
        framework_config = self.get_config(ConfigType.FRAMEWORK)
        return framework_config.get(key, default) if framework_config else default

    def get_performance_threshold(self, metric: str) -> float:
        """
        Obtém limite de performance para métrica específica.
        
        Args:
            metric: Nome da métrica
            
        Returns:
            Valor limite da métrica
        """
        thresholds = self.get_test_setting("performance_thresholds", {})
        return thresholds.get(metric, 1.0)

    def override_config(self, section: str, key: str, value: Any) -> None:
        """
        Substitui temporariamente uma configuração.
        
        Args:
            section: Seção da configuração
            key: Chave a ser modificada
            value: Novo valor
        """
        config = self.load_config()
        if section in config:
            config[section][key] = value
            self._logger.info(f"Configuração sobrescrita: {section}.{key} = {value}")

    def save_config(self, config_data: Dict[str, Any] = None) -> bool:
        """
        Salva configurações no arquivo.
        
        Args:
            config_data: Dados para salvar (usa cache se None)
            
        Returns:
            True se salvo com sucesso
        """
        try:
            data_to_save = config_data or self._config_cache
            if data_to_save is None:
                return False
                
            # Criar diretório se não existir
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                
            self._logger.info(f"Configurações salvas em {self.config_file}")
            return True
            
        except Exception as e:
            self._logger.error(f"Erro ao salvar configurações: {e}")
            return False

    def create_test_settings(self) -> TestSettings:
        """
        Cria objeto TestSettings a partir das configurações.
        
        Returns:
            Objeto TestSettings configurado
        """
        framework_config = self.get_config(ConfigType.FRAMEWORK) or {}
        
        return TestSettings(
            logging_level=framework_config.get("logging_level", "INFO"),
            temp_cleanup=framework_config.get("temp_cleanup", True),
            skip_unavailable_modules=framework_config.get("skip_unavailable_modules", True),
            timeout_seconds=framework_config.get("timeout_seconds", 30),
            performance_thresholds=framework_config.get("performance_thresholds", {})
        )

    def create_mock_config(self) -> MockConfig:
        """
        Cria objeto MockConfig a partir das configurações.
        
        Returns:
            Objeto MockConfig configurado
        """
        mock_config = self.get_config(ConfigType.MOCK) or {}
        
        return MockConfig(
            performance_manager=mock_config.get("performance_manager", {}),
            audio_manager=mock_config.get("audio_manager", {}),
            validation_tests=mock_config.get("validation_tests", {})
        )

    def get_test_suites(self, suite_type: str = None) -> List[str]:
        """
        Obtém lista de suítes de teste.
        
        Args:
            suite_type: Tipo específico de suíte
            
        Returns:
            Lista de nomes de classes de teste
        """
        suites_config = self.get_config(ConfigType.SUITES) or {}
        
        if suite_type:
            return suites_config.get(suite_type, [])
        
        # Retorna todas as suítes
        all_suites = []
        for suite_list in suites_config.values():
            if isinstance(suite_list, list):
                all_suites.extend(suite_list)
        
        return all_suites

    def is_environment_variable_set(self, var_name: str) -> bool:
        """
        Verifica se variável de ambiente está definida.
        
        Args:
            var_name: Nome da variável
            
        Returns:
            True se definida
        """
        return var_name in os.environ

    def get_from_env_or_config(self, env_var: str, config_section: str, 
                              config_key: str, default: Any = None) -> Any:
        """
        Obtém valor da variável de ambiente ou configuração.
        
        Args:
            env_var: Nome da variável de ambiente
            config_section: Seção da configuração
            config_key: Chave da configuração
            default: Valor padrão
            
        Returns:
            Valor encontrado ou padrão
        """
        # Primeiro tenta variável de ambiente
        env_value = os.environ.get(env_var)
        if env_value is not None:
            # Tentar converter tipos comuns
            if env_value.lower() in ('true', 'false'):
                return env_value.lower() == 'true'
            try:
                # Tentar número
                if '.' in env_value:
                    return float(env_value)
                else:
                    return int(env_value)
            except ValueError:
                return env_value
        
        # Senão, usa configuração
        return self.get_config(config_section, config_key) or default


# Instância global do gerenciador
_config_manager = None

def get_config_manager() -> TestConfigManager:
    """
    Obtém instância global do gerenciador de configurações.
    
    Returns:
        TestConfigManager: Instância do gerenciador
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = TestConfigManager()
    return _config_manager

# Funções de conveniência
def get_mock_config(module: str) -> Dict[str, Any]:
    """Função de conveniência para obter configuração de mock."""
    return get_config_manager().get_mock_config(module)

def get_test_setting(key: str, default: Any = None) -> Any:
    """Função de conveniência para obter configuração de teste."""
    return get_config_manager().get_test_setting(key, default)

def get_performance_threshold(metric: str) -> float:
    """Função de conveniência para obter limite de performance."""
    return get_config_manager().get_performance_threshold(metric)

def get_test_suites(suite_type: str = None) -> List[str]:
    """Função de conveniência para obter suítes de teste."""
    return get_config_manager().get_test_suites(suite_type)

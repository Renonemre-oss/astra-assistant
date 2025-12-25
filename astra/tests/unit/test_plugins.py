#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Sistema de Plugins para Testes
Permite extensão dinâmica do framework de testes
"""

import os
import sys
import importlib
import unittest
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, Callable
import logging

# Adicionar o diretório de testes ao path para importações locais
sys.path.append(str(Path(__file__).parent))
from test_config import get_config_manager, get_test_setting


class TestPlugin(ABC):
    """Classe base abstrata para plugins de teste."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome identificador do plugin."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Versão do plugin."""
        pass
    
    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """Lista de dependências necessárias."""
        pass
    
    @abstractmethod
    def setup(self) -> bool:
        """
        Configuração inicial do plugin.
        
        Returns:
            True se setup foi bem-sucedido
        """
        pass
    
    @abstractmethod
    def get_test_classes(self) -> List[Type[unittest.TestCase]]:
        """
        Retorna classes de teste fornecidas pelo plugin.
        
        Returns:
            Lista de classes de teste
        """
        pass
    
    @abstractmethod
    def teardown(self) -> None:
        """Limpeza final do plugin."""
        pass
    
    def is_available(self) -> bool:
        """
        Verifica se plugin pode ser carregado.
        
        Returns:
            True se todas as dependências estão disponíveis
        """
        for dependency in self.dependencies:
            try:
                importlib.import_module(dependency)
            except ImportError:
                return False
        return True


class PluginManager:
    """Gerenciador de plugins para testes."""
    
    def __init__(self):
        """Inicializa o gerenciador de plugins."""
        self._plugins: Dict[str, TestPlugin] = {}
        self._logger = logging.getLogger(f"{__name__}.PluginManager")
        
        # Caminhos para buscar plugins
        self.plugin_directories = [
            Path(__file__).parent / "plugins",
            Path.cwd() / "test_plugins",
        ]
        
        # Adicionar caminhos de variáveis de ambiente
        env_paths = os.environ.get("ALEX_TEST_PLUGIN_PATHS", "")
        for path_str in env_paths.split(os.pathsep):
            if path_str.strip():
                self.plugin_directories.append(Path(path_str.strip()))
    
    def discover_plugins(self) -> List[str]:
        """
        Descobre plugins disponíveis nos diretórios configurados.
        
        Returns:
            Lista de nomes de plugins encontrados
        """
        discovered = []
        
        for plugin_dir in self.plugin_directories:
            if not plugin_dir.exists():
                continue
                
            self._logger.info(f"Procurando plugins em: {plugin_dir}")
            
            # Adicionar diretório ao path temporariamente
            if str(plugin_dir) not in sys.path:
                sys.path.insert(0, str(plugin_dir))
            
            try:
                # Buscar arquivos .py que não começam com _
                for plugin_file in plugin_dir.glob("*.py"):
                    if plugin_file.name.startswith("_"):
                        continue
                    
                    plugin_name = plugin_file.stem
                    
                    try:
                        # Tentar importar o módulo
                        module = importlib.import_module(plugin_name)
                        
                        # Procurar por classes que herdam de TestPlugin
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            
                            if (isinstance(attr, type) and 
                                issubclass(attr, TestPlugin) and 
                                attr is not TestPlugin):
                                
                                discovered.append(plugin_name)
                                self._logger.info(f"Plugin descoberto: {plugin_name}")
                                break
                                
                    except Exception as e:
                        self._logger.warning(f"Erro ao descobrir plugin {plugin_name}: {e}")
                        
            finally:
                # Remover do path
                if str(plugin_dir) in sys.path:
                    sys.path.remove(str(plugin_dir))
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Carrega um plugin específico.
        
        Args:
            plugin_name: Nome do plugin a carregar
            
        Returns:
            True se carregamento foi bem-sucedido
        """
        if plugin_name in self._plugins:
            self._logger.info(f"Plugin {plugin_name} já carregado")
            return True
        
        try:
            # Tentar importar o módulo do plugin
            module = importlib.import_module(plugin_name)
            
            # Encontrar a classe do plugin
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (isinstance(attr, type) and 
                    issubclass(attr, TestPlugin) and 
                    attr is not TestPlugin):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                self._logger.error(f"Nenhuma classe TestPlugin encontrada em {plugin_name}")
                return False
            
            # Criar instância do plugin
            plugin_instance = plugin_class()
            
            # Verificar disponibilidade
            if not plugin_instance.is_available():
                self._logger.warning(
                    f"Plugin {plugin_name} não está disponível (dependências ausentes)"
                )
                return False
            
            # Executar setup
            if not plugin_instance.setup():
                self._logger.error(f"Falha no setup do plugin {plugin_name}")
                return False
            
            # Registrar plugin
            self._plugins[plugin_name] = plugin_instance
            self._logger.info(
                f"Plugin carregado: {plugin_instance.name} v{plugin_instance.version}"
            )
            
            return True
            
        except Exception as e:
            self._logger.error(f"Erro ao carregar plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """
        Carrega todos os plugins descobertos.
        
        Returns:
            Dicionário com resultado do carregamento de cada plugin
        """
        results = {}
        discovered = self.discover_plugins()
        
        for plugin_name in discovered:
            results[plugin_name] = self.load_plugin(plugin_name)
        
        return results
    
    def get_plugin(self, plugin_name: str) -> Optional[TestPlugin]:
        """
        Obtém instância de um plugin carregado.
        
        Args:
            plugin_name: Nome do plugin
            
        Returns:
            Instância do plugin ou None se não encontrado
        """
        return self._plugins.get(plugin_name)
    
    def get_loaded_plugins(self) -> Dict[str, TestPlugin]:
        """
        Retorna todos os plugins carregados.
        
        Returns:
            Dicionário de plugins carregados
        """
        return self._plugins.copy()
    
    def get_test_classes_from_plugins(self) -> List[Type[unittest.TestCase]]:
        """
        Obtém todas as classes de teste de plugins carregados.
        
        Returns:
            Lista de classes de teste
        """
        test_classes = []
        
        for plugin in self._plugins.values():
            try:
                plugin_classes = plugin.get_test_classes()
                test_classes.extend(plugin_classes)
            except Exception as e:
                self._logger.error(f"Erro ao obter classes de teste do plugin {plugin.name}: {e}")
        
        return test_classes
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Descarrega um plugin.
        
        Args:
            plugin_name: Nome do plugin a descarregar
            
        Returns:
            True se descarregamento foi bem-sucedido
        """
        if plugin_name not in self._plugins:
            self._logger.warning(f"Plugin {plugin_name} não está carregado")
            return False
        
        try:
            plugin = self._plugins[plugin_name]
            plugin.teardown()
            del self._plugins[plugin_name]
            
            self._logger.info(f"Plugin descarregado: {plugin_name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Erro ao descarregar plugin {plugin_name}: {e}")
            return False
    
    def unload_all_plugins(self) -> None:
        """Descarrega todos os plugins."""
        plugin_names = list(self._plugins.keys())
        
        for plugin_name in plugin_names:
            self.unload_plugin(plugin_name)
    
    def get_plugin_info(self) -> List[Dict[str, str]]:
        """
        Obtém informações sobre todos os plugins carregados.
        
        Returns:
            Lista de dicionários com informações dos plugins
        """
        info = []
        
        for plugin in self._plugins.values():
            info.append({
                "name": plugin.name,
                "version": plugin.version,
                "dependencies": ", ".join(plugin.dependencies),
                "available": "Yes" if plugin.is_available() else "No"
            })
        
        return info


class PluginTestSuite:
    """Suite de testes que inclui plugins."""
    
    def __init__(self, plugin_manager: Optional[PluginManager] = None):
        """
        Inicializa a suite de testes com plugins.
        
        Args:
            plugin_manager: Gerenciador de plugins (cria um novo se None)
        """
        self.plugin_manager = plugin_manager or PluginManager()
        self._logger = logging.getLogger(f"{__name__}.PluginTestSuite")
    
    def create_test_suite(self, load_plugins: bool = True) -> unittest.TestSuite:
        """
        Cria suite de testes incluindo plugins.
        
        Args:
            load_plugins: Se deve carregar plugins automaticamente
            
        Returns:
            Suite de testes configurada
        """
        suite = unittest.TestSuite()
        
        if load_plugins:
            # Carregar plugins se solicitado
            results = self.plugin_manager.load_all_plugins()
            loaded_count = sum(1 for success in results.values() if success)
            self._logger.info(f"Carregados {loaded_count} de {len(results)} plugins")
        
        # Adicionar testes dos plugins
        plugin_test_classes = self.plugin_manager.get_test_classes_from_plugins()
        
        for test_class in plugin_test_classes:
            suite.addTest(unittest.makeSuite(test_class))
            self._logger.debug(f"Adicionada classe de teste: {test_class.__name__}")
        
        return suite
    
    def run_tests(self, verbosity: int = 2) -> unittest.TextTestResult:
        """
        Executa todos os testes incluindo plugins.
        
        Args:
            verbosity: Nível de verbosidade dos testes
            
        Returns:
            Resultado dos testes
        """
        suite = self.create_test_suite()
        runner = unittest.TextTestRunner(verbosity=verbosity)
        
        self._logger.info("Iniciando execução de testes com plugins")
        result = runner.run(suite)
        
        # Descarregar plugins após execução
        self.plugin_manager.unload_all_plugins()
        
        return result


# Instância global do gerenciador de plugins
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """
    Obtém instância global do gerenciador de plugins.
    
    Returns:
        PluginManager: Instância do gerenciador
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager

# Funções de conveniência
def load_plugin(plugin_name: str) -> bool:
    """Função de conveniência para carregar plugin."""
    return get_plugin_manager().load_plugin(plugin_name)

def get_plugin(plugin_name: str) -> Optional[TestPlugin]:
    """Função de conveniência para obter plugin."""
    return get_plugin_manager().get_plugin(plugin_name)
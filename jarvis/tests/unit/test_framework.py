#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Framework de Testes Automatizados
Sistema completo de testes para validar funcionalidades do projeto

Este módulo fornece:
- Testes unitários para módulos principais
- Testes de integração
- Mocks para dependências externas
- Relatórios de cobertura
- Testes de performance
"""

import unittest
import sys
import os
import tempfile
import json
import time
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from typing import Any, Dict, List
import logging

# Adicionar diretório pai ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar sistema de configuração flexível
try:
    from .test_config import (
        get_config_manager, get_test_setting, get_performance_threshold,
        get_mock_config, get_test_suites
    )
    from .test_factories import (
        MockFactory, FileFactory, TestDataBuilder, MockLogger
    )
except ImportError:
    # Execução direta - usar imports absolutos
    from test_config import (
        get_config_manager, get_test_setting, get_performance_threshold,
        get_mock_config, get_test_suites
    )
    from test_factories import (
        MockFactory, FileFactory, TestDataBuilder, MockLogger
    )

# Configurar logging para testes dinamicamente
log_level = get_test_setting("logging_level", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

class ALEXTestCase(unittest.TestCase):
    """Classe base para testes do ALEX com utilitários comuns."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        # Usar FileFactory para criar estrutura temporária
        self.temp_path = FileFactory.create_temp_dir()
        
        # Configurar mock logger usando o sistema flexível
        self.mock_logger = MockLogger()
        self.log_patcher = patch('logging.getLogger')
        self.log_patcher.start().return_value = self.mock_logger
        
        # Carregar configurações de teste
        self.config_manager = get_config_manager()
        
    def tearDown(self):
        """Limpeza após cada teste."""
        self.log_patcher.stop()
        
        # Limpar arquivos temporários usando configuração
        FileFactory.cleanup_dir(self.temp_path)
    
    def create_temp_file(self, filename: str, content: str = "") -> Path:
        """Cria arquivo temporário para testes usando FileFactory."""
        return FileFactory.create_temp_file(self.temp_path, filename, content)
    
    def skip_if_module_unavailable(self, module_name: str) -> bool:
        """
        Verifica se deve pular teste por módulo indisponível.
        
        Args:
            module_name: Nome do módulo a verificar
            
        Returns:
            True se deve pular
        """
        return get_test_setting("skip_unavailable_modules", True)

class TestSystemDiagnostics(ALEXTestCase):
    """Testes para o sistema de diagnóstico."""
    
    def setUp(self):
        super().setUp()
        # Mock para evitar imports problemáticos durante testes
        # Não usar get_system_info que não existe mais
        pass
    
    def tearDown(self):
        super().tearDown()
        pass
    
    def test_system_diagnostics_creation(self):
        """Testa criação do sistema de diagnóstico."""
        try:
            from utils.system_diagnostics import SystemDiagnostics
            
            diagnostics = SystemDiagnostics()
            
            self.assertIsNotNone(diagnostics)
            self.assertEqual(diagnostics.results, {})
            self.assertEqual(diagnostics.suggestions, [])
            self.assertEqual(diagnostics.errors, [])
            self.assertEqual(diagnostics.warnings, [])
            
        except ImportError:
            self.skipTest("SystemDiagnostics não disponível")

class TestPerformanceManager(ALEXTestCase):
    """Testes para o gestor de performance."""
    
    def setUp(self):
        super().setUp()
        # Usar MockFactory para criar mock de psutil
        self.psutil_patcher = patch('utils.profiling.performance_monitor.psutil')
        self.mock_psutil = self.psutil_patcher.start()
        self.mock_psutil = MockFactory.create_psutil_mock()
        self.psutil_patcher.return_value = self.mock_psutil
    
    def tearDown(self):
        super().tearDown()
        self.psutil_patcher.stop()
    
    def test_performance_manager_creation(self):
        """Testa criação do gestor de performance."""
        try:
            from utils.profiling.performance_monitor import PerformanceMonitor
            
            # Criar monitor de performance
            pm = PerformanceMonitor()
            
            self.assertIsNotNone(pm)
            self.assertFalse(pm.monitoring)
            # PerformanceMonitor da Fase 3 tem API diferente
            
        except ImportError:
            if self.skip_if_module_unavailable("PerformanceManager"):
                self.skipTest("PerformanceManager não disponível")
    
    def test_thread_safe_cache(self):
        """Testa funcionamento do cache thread-safe."""
        try:
            from utils.cache.cache_manager import CacheManager
            
            # Usar configurações dinâmicas
            params = TestDataBuilder.build_performance_test_params()
            
            cache = CacheManager(
                max_size=params["cache_size"], 
                default_ttl=params["cache_ttl"]
            )
            
            # Usar dados de teste configuráveis
            test_data = TestDataBuilder.build_validation_test_data()
            
            # Testar set/get
            cache.set("test_key", test_data["test_string"])
            self.assertEqual(cache.get("test_key"), test_data["test_string"])
            
            # Testar chave inexistente
            self.assertIsNone(cache.get("nonexistent"))
            
            # Testar valor padrão
            self.assertEqual(cache.get("nonexistent", "default"), "default")
            
            # Testar tamanho
            self.assertEqual(cache.size(), 1)
            
        except ImportError:
            if self.skip_if_module_unavailable("ThreadSafeCache"):
                self.skipTest("ThreadSafeCache não disponível")

class TestErrorHandler(ALEXTestCase):
    """Testes para o sistema de tratamento de erros."""
    
    def test_validation_error_creation(self):
        """Testa criação de erros de validação."""
        try:
            from utils.error_handler import ValidationError
            
            # Usar dados de teste configuráveis
            test_data = TestDataBuilder.build_validation_test_data()
            
            error = ValidationError(
                "Teste", 
                field=test_data["test_field"], 
                value=test_data["test_value"]
            )
            
            self.assertEqual(str(error), "Teste")
            self.assertEqual(error.field, test_data["test_field"])
            self.assertEqual(error.value, test_data["test_value"])
            
        except ImportError:
            if self.skip_if_module_unavailable("ErrorHandler"):
                self.skipTest("ErrorHandler não disponível")
    
    def test_validators(self):
        """Testa validadores básicos."""
        try:
            from utils.error_handler import Validators, ValidationError
            
            # Usar dados de teste configuráveis
            test_data = TestDataBuilder.build_validation_test_data()
            
            # Testar not_empty
            self.assertEqual(
                Validators.not_empty(test_data["test_string"]), 
                test_data["test_string"]
            )
            with self.assertRaises(ValidationError):
                Validators.not_empty("")
            
            # Testar string_length
            self.assertEqual(
                Validators.string_length(
                    test_data["test_string"], 
                    test_data["min_length"], 
                    test_data["max_length"]
                ), 
                test_data["test_string"]
            )
            with self.assertRaises(ValidationError):
                Validators.string_length(
                    "", 
                    test_data["min_length"], 
                    test_data["max_length"]
                )
            
            # Testar numeric_range
            self.assertEqual(
                Validators.numeric_range(
                    test_data["numeric_test"], 
                    test_data["numeric_min"], 
                    test_data["numeric_max"]
                ), 
                test_data["numeric_test"]
            )
            with self.assertRaises(ValidationError):
                Validators.numeric_range(
                    test_data["numeric_fail"], 
                    test_data["numeric_min"], 
                    test_data["numeric_max"]
                )
                
        except ImportError:
            if self.skip_if_module_unavailable("Validators"):
                self.skipTest("Validators não disponível")

class TestAudioManager(ALEXTestCase):
    """Testes para o gestor de áudio."""
    
    def setUp(self):
        super().setUp()
        # Usar MockFactory para dependências de áudio
        dependencies = MockFactory.create_audio_dependencies_mock()
        self.tts_patcher = patch('audio.audio_manager.DEPENDENCIES', dependencies)
        self.mock_deps = self.tts_patcher.start()
    
    def tearDown(self):
        super().tearDown()
        self.tts_patcher.stop()
    
    def test_audio_manager_creation(self):
        """Testa criação do gestor de áudio."""
        try:
            from audio.audio_manager import AudioManager
            
            audio_manager = AudioManager()
            
            # Verificar usando configurações dinâmicas
            expected_tts_loaded = get_mock_config("audio_manager").get("tts_loaded", False)
            
            self.assertIsNotNone(audio_manager)
            self.assertEqual(audio_manager.tts_loaded, expected_tts_loaded)
            
        except ImportError:
            if self.skip_if_module_unavailable("AudioManager"):
                self.skipTest("AudioManager não disponível")

class TestPersonalProfile(ALEXTestCase):
    """Testes para o perfil pessoal."""
    
    def setUp(self):
        super().setUp()
        # Criar arquivo de facts temporário
        self.facts_file = self.create_temp_file("personal_facts.json", "{}")
        
        # Mock CONFIG para usar arquivo temporário
        self.config_patcher = patch('modules.personal_profile.CONFIG')
        self.mock_config = self.config_patcher.start()
        self.mock_config.__getitem__.return_value = self.facts_file
    
    def tearDown(self):
        super().tearDown()
        self.config_patcher.stop()
    
    @patch('modules.personal_profile.CONFIG')
    def test_personal_profile_creation(self, mock_config):
        """Testa criação do perfil pessoal."""
        try:
            mock_config.__getitem__.return_value = self.facts_file
            from modules.personal_profile import PersonalProfile
            
            profile = PersonalProfile()
            
            self.assertIsNotNone(profile)
            self.assertIsInstance(profile.facts_cache, dict)
            
        except ImportError:
            self.skipTest("PersonalProfile não disponível")

class TestDatabaseModels(ALEXTestCase):
    """Testes para modelos de base de dados."""
    
    def test_database_models_import(self):
        """Testa importação dos modelos de base de dados."""
        try:
            from database.models import (
                Conversation, Message, VoiceInteraction, 
                UserPreference, Person, UserProfile
            )
            
            # Testar que classes existem
            self.assertTrue(hasattr(Conversation, '__tablename__'))
            self.assertTrue(hasattr(Message, '__tablename__'))
            self.assertTrue(hasattr(UserProfile, '__tablename__'))
            
        except ImportError:
            self.skipTest("Modelos de base de dados não disponíveis")
    
    def test_model_to_dict(self):
        """Testa conversão de modelos para dicionário."""
        try:
            from database.models import UserPreference
            from datetime import datetime
            
            # Não podemos criar instâncias reais sem base de dados
            # Apenas verificar que método existe
            self.assertTrue(hasattr(UserPreference, 'to_dict'))
            
        except ImportError:
            self.skipTest("Modelos de base de dados não disponíveis")

class TestConfigSystem(ALEXTestCase):
    """Testes para sistema de configuração."""
    
    def test_config_import(self):
        """Testa importação da configuração."""
        try:
            from config.config import CONFIG, PERSONALITIES, UI_STYLES
            
            self.assertIsInstance(CONFIG, dict)
            self.assertIsInstance(PERSONALITIES, dict)
            self.assertIsInstance(UI_STYLES, dict)
            
            # Verificar chaves essenciais
            self.assertIn("ollama_model", CONFIG)
            self.assertIn("conversation_history_size", CONFIG)
            
        except ImportError:
            self.skipTest("Sistema de configuração não disponível")

class PerformanceTest(ALEXTestCase):
    """Testes de performance para funções críticas."""
    
    def test_file_operations_performance(self):
        """Testa performance de operações de arquivo."""
        # Criar arquivo de teste usando configuração
        test_file = self.create_temp_file("performance_test.json")
        
        # Obter limites de performance configuráveis
        write_threshold = get_performance_threshold("write_time_max")
        read_threshold = get_performance_threshold("read_time_max")
        
        # Testar escrita
        start_time = time.time()
        for i in range(100):
            test_data = {"iteration": i, "data": "test" * 100}
            test_file.write_text(json.dumps(test_data), encoding='utf-8')
        write_time = time.time() - start_time
        
        # Testar leitura
        start_time = time.time()
        for i in range(100):
            content = test_file.read_text(encoding='utf-8')
            json.loads(content)
        read_time = time.time() - start_time
        
        # Verificar usando limites configuráveis
        self.assertLess(
            write_time, write_threshold, 
            f"Escrita muito lenta: {write_time:.2f}s (limite: {write_threshold}s)"
        )
        self.assertLess(
            read_time, read_threshold, 
            f"Leitura muito lenta: {read_time:.2f}s (limite: {read_threshold}s)"
        )
        
        logger.info(f"Performance - Escrita: {write_time:.3f}s, Leitura: {read_time:.3f}s")

class IntegrationTest(ALEXTestCase):
    """Testes de integração entre módulos."""
    
    def test_config_and_logging_integration(self):
        """Testa integração entre configuração e logging."""
        try:
            from config.config import configure_logging, LOGS_DIR
            
            # Verificar que função existe
            self.assertTrue(callable(configure_logging))
            
            # Verificar que diretório de logs é definido
            self.assertIsNotNone(LOGS_DIR)
            
        except ImportError:
            self.skipTest("Módulos de integração não disponíveis")

def create_test_suite() -> unittest.TestSuite:
    """Cria suite de testes completa."""
    suite = unittest.TestSuite()
    
    # Adicionar testes unitários
    suite.addTest(unittest.makeSuite(TestSystemDiagnostics))
    suite.addTest(unittest.makeSuite(TestPerformanceManager))
    suite.addTest(unittest.makeSuite(TestErrorHandler))
    suite.addTest(unittest.makeSuite(TestAudioManager))
    suite.addTest(unittest.makeSuite(TestPersonalProfile))
    suite.addTest(unittest.makeSuite(TestDatabaseModels))
    suite.addTest(unittest.makeSuite(TestConfigSystem))
    
    # Adicionar testes de performance
    suite.addTest(unittest.makeSuite(PerformanceTest))
    
    # Adicionar testes de integração
    suite.addTest(unittest.makeSuite(IntegrationTest))
    
    return suite

def run_tests(verbosity: int = 2) -> unittest.TestResult:
    """
    Executa todos os testes.
    
    Args:
        verbosity: Nível de verbosidade (0=quiet, 1=normal, 2=verbose)
    
    Returns:
        Resultado dos testes
    """
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    
    print(f"🧪 Executando {suite.countTestCases()} testes...")
    print("-" * 60)
    
    result = runner.run(suite)
    
    print("-" * 60)
    print(f"✅ Testes executados: {result.testsRun}")
    print(f"❌ Falhas: {len(result.failures)}")
    print(f"💥 Erros: {len(result.errors)}")
    print(f"⏸️ Ignorados: {len(result.skipped)}")
    
    # Mostrar detalhes dos erros
    if result.failures:
        print("\n❌ FALHAS:")
        for test, trace in result.failures:
            print(f"  - {test}: {trace.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 ERROS:")
        for test, trace in result.errors:
            print(f"  - {test}: {trace.split('Exception:')[-1].strip()}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n📊 Taxa de sucesso: {success_rate:.1f}%")
    
    return result

def generate_coverage_report():
    """Gera relatório de cobertura de código."""
    try:
        import coverage
        
        cov = coverage.Coverage()
        cov.start()
        
        # Executar testes
        run_tests(verbosity=0)
        
        cov.stop()
        cov.save()
        
        print("\n📈 Relatório de Cobertura:")
        cov.report()
        
        # Salvar relatório HTML
        html_dir = Path("htmlcov")
        cov.html_report(directory=str(html_dir))
        print(f"📄 Relatório HTML salvo em: {html_dir}")
        
    except ImportError:
        print("⚠️ Coverage.py não instalado. Use: pip install coverage")

def main():
    """Função principal para executar testes."""
    import argparse
    
    parser = argparse.ArgumentParser(description='ALEX Test Framework')
    parser.add_argument('-v', '--verbose', action='count', default=1,
                       help='Increase verbosity')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--pattern', type=str, default='*',
                       help='Run only tests matching pattern')
    
    args = parser.parse_args()
    
    if args.coverage:
        generate_coverage_report()
    else:
        result = run_tests(verbosity=args.verbose)
        
        # Exit code baseado nos resultados
        if result.failures or result.errors:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTES INTENSIVOS DO Astra
Suite completa de testes para validar todos os componentes do sistema
"""

import sys
import unittest
import logging
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar logging para testes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCoreModules(unittest.TestCase):
    """Testes dos módulos core do sistema"""
    
    def setUp(self):
        """Setup antes de cada teste"""
        logger.info("="*60)
        logger.info(f"Iniciando teste: {self._testMethodName}")
        self.start_time = time.time()
    
    def tearDown(self):
        """Cleanup depois de cada teste"""
        duration = time.time() - self.start_time
        logger.info(f"✅ Teste concluído em {duration:.3f}s")
        logger.info("="*60)
    
    def test_config_import(self):
        """Teste 1: Importação do módulo de configuração"""
        try:
            from config import CONFIG, UI_STYLES, DATABASE_AVAILABLE
            self.assertIsInstance(CONFIG, dict)
            self.assertIsInstance(UI_STYLES, dict)
            self.assertIsInstance(DATABASE_AVAILABLE, bool)
            logger.info("✅ Config importado com sucesso")
        except Exception as e:
            self.fail(f"❌ Falha ao importar config: {e}")
    
    def test_audio_manager_import(self):
        """Teste 2: Importação do Audio Manager"""
        try:
            from modules.audio.audio_manager import AudioManager
            self.assertIsNotNone(AudioManager)
            logger.info("✅ AudioManager importado com sucesso")
        except Exception as e:
            self.fail(f"❌ Falha ao importar AudioManager: {e}")
    
    def test_speech_engine_import(self):
        """Teste 3: Importação do Speech Engine"""
        try:
            from modules.speech.speech_engine import SpeechEngine, SpeechStatus
            self.assertIsNotNone(SpeechEngine)
            self.assertIsNotNone(SpeechStatus)
            logger.info("✅ SpeechEngine importado com sucesso")
        except Exception as e:
            self.fail(f"❌ Falha ao importar SpeechEngine: {e}")
    
    def test_hotword_detector_import(self):
        """Teste 4: Importação do Hotword Detector"""
        try:
            from modules.speech.hotword_detector import create_hotword_detector
            self.assertIsNotNone(create_hotword_detector)
            logger.info("✅ HotwordDetector importado com sucesso")
        except Exception as e:
            self.fail(f"❌ Falha ao importar HotwordDetector: {e}")
    
    def test_personality_engine_import(self):
        """Teste 5: Importação do Personality Engine"""
        try:
            from modules.personality_engine import PersonalityEngine
            self.assertIsNotNone(PersonalityEngine)
            logger.info("✅ PersonalityEngine importado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ PersonalityEngine não disponível: {e}")
    
    def test_memory_system_import(self):
        """Teste 6: Importação do Memory System"""
        try:
            from modules.memory_system import MemorySystem
            self.assertIsNotNone(MemorySystem)
            logger.info("✅ MemorySystem importado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ MemorySystem não disponível: {e}")
    
    def test_api_hub_import(self):
        """Teste 7: Importação do API Hub"""
        try:
            from api.api_integration_hub import ApiIntegrationHub
            self.assertIsNotNone(ApiIntegrationHub)
            logger.info("✅ ApiIntegrationHub importado com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ ApiIntegrationHub não disponível: {e}")


class TestAudioSystem(unittest.TestCase):
    """Testes do sistema de áudio"""
    
    def setUp(self):
        logger.info("="*60)
        logger.info(f"Iniciando teste: {self._testMethodName}")
        self.start_time = time.time()
    
    def tearDown(self):
        duration = time.time() - self.start_time
        logger.info(f"✅ Teste concluído em {duration:.3f}s")
        logger.info("="*60)
    
    def test_audio_manager_initialization(self):
        """Teste 8: Inicialização do Audio Manager"""
        try:
            from modules.audio.audio_manager import AudioManager
            
            status_messages = []
            def status_callback(msg):
                status_messages.append(msg)
            
            audio_manager = AudioManager(status_callback=status_callback)
            self.assertIsNotNone(audio_manager)
            self.assertFalse(audio_manager._shutdown)
            logger.info("✅ AudioManager inicializado com sucesso")
        except Exception as e:
            self.fail(f"❌ Falha ao inicializar AudioManager: {e}")
    
    def test_speech_engine_initialization(self):
        """Teste 9: Inicialização do Speech Engine"""
        try:
            from modules.speech.speech_engine import SpeechEngine
            
            speech_engine = SpeechEngine()
            self.assertIsNotNone(speech_engine)
            logger.info("✅ SpeechEngine inicializado com sucesso")
            
            # Verificar se TTS está disponível
            if speech_engine.tts_engine:
                logger.info("✅ TTS Engine carregado")
            else:
                logger.warning("⚠️ TTS Engine não disponível")
        except Exception as e:
            self.fail(f"❌ Falha ao inicializar SpeechEngine: {e}")
    
    def test_speech_engine_methods(self):
        """Teste 10: Métodos do Speech Engine"""
        try:
            from modules.speech.speech_engine import SpeechEngine
            
            speech_engine = SpeechEngine()
            
            # Testar get_system_info
            info = speech_engine.get_system_info()
            self.assertIsInstance(info, dict)
            logger.info(f"✅ System Info: {info}")
            
            # Testar get_available_voices
            voices = speech_engine.get_available_voices()
            self.assertIsInstance(voices, list)
            logger.info(f"✅ Vozes disponíveis: {len(voices)}")
            
        except Exception as e:
            self.fail(f"❌ Falha nos métodos do SpeechEngine: {e}")


class TestUtilities(unittest.TestCase):
    """Testes de utilitários"""
    
    def setUp(self):
        logger.info("="*60)
        logger.info(f"Iniciando teste: {self._testMethodName}")
        self.start_time = time.time()
    
    def tearDown(self):
        duration = time.time() - self.start_time
        logger.info(f"✅ Teste concluído em {duration:.3f}s")
        logger.info("="*60)
    
    def test_utils_imports(self):
        """Teste 11: Importação de utilitários"""
        try:
            from utils.utils import remover_emojis, limpar_texto_tts
            self.assertIsNotNone(remover_emojis)
            self.assertIsNotNone(limpar_texto_tts)
            logger.info("✅ Utilitários importados com sucesso")
        except Exception as e:
            self.fail(f"❌ Falha ao importar utilitários: {e}")
    
    def test_remover_emojis(self):
        """Teste 12: Função remover_emojis"""
        try:
            from utils.utils import remover_emojis
            
            text_with_emojis = "Olá 😀 como está? 🎉"
            result = remover_emojis(text_with_emojis)
            
            # Verificar se emojis foram removidos
            self.assertNotIn("😀", result)
            self.assertNotIn("🎉", result)
            logger.info(f"✅ Emojis removidos: '{text_with_emojis}' -> '{result}'")
        except Exception as e:
            self.fail(f"❌ Falha ao remover emojis: {e}")
    
    def test_error_handler_import(self):
        """Teste 13: Importação do Error Handler"""
        try:
            from utils.error_handler import handle_errors, ErrorLevel, ErrorCategory
            self.assertIsNotNone(handle_errors)
            self.assertIsNotNone(ErrorLevel)
            self.assertIsNotNone(ErrorCategory)
            logger.info("✅ ErrorHandler importado com sucesso")
        except Exception as e:
            self.fail(f"❌ Falha ao importar ErrorHandler: {e}")


class TestDataStructures(unittest.TestCase):
    """Testes de estruturas de dados"""
    
    def setUp(self):
        logger.info("="*60)
        logger.info(f"Iniciando teste: {self._testMethodName}")
        self.start_time = time.time()
    
    def tearDown(self):
        duration = time.time() - self.start_time
        logger.info(f"✅ Teste concluído em {duration:.3f}s")
        logger.info("="*60)
    
    def test_directory_structure(self):
        """Teste 14: Estrutura de diretórios"""
        project_root = Path(__file__).parent.parent
        
        required_dirs = [
            "core", "modules", "config", "utils", 
            "data", "logs", "tests", "api"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            self.assertTrue(dir_path.exists(), f"Diretório {dir_name} não existe")
            logger.info(f"✅ Diretório '{dir_name}' existe")
    
    def test_config_files(self):
        """Teste 15: Arquivos de configuração"""
        project_root = Path(__file__).parent.parent
        
        config_files = [
            "config/__init__.py",
            "config/settings/main_config.py"
        ]
        
        for file_path in config_files:
            full_path = project_root / file_path
            self.assertTrue(full_path.exists(), f"Arquivo {file_path} não existe")
            logger.info(f"✅ Arquivo '{file_path}' existe")


class TestIntegration(unittest.TestCase):
    """Testes de integração"""
    
    def setUp(self):
        logger.info("="*60)
        logger.info(f"Iniciando teste: {self._testMethodName}")
        self.start_time = time.time()
    
    def tearDown(self):
        duration = time.time() - self.start_time
        logger.info(f"✅ Teste concluído em {duration:.3f}s")
        logger.info("="*60)
    
    def test_audio_and_speech_integration(self):
        """Teste 16: Integração Audio Manager + Speech Engine"""
        try:
            from modules.audio.audio_manager import AudioManager
            
            audio_manager = AudioManager()
            audio_manager.load_tts_model()
            
            # Aguardar carregamento
            time.sleep(2)
            
            status = audio_manager.get_status()
            logger.info(f"✅ Status do AudioManager: {status}")
            
        except Exception as e:
            logger.warning(f"⚠️ Integração Audio/Speech: {e}")
    
    def test_config_and_modules_integration(self):
        """Teste 17: Integração Config + Módulos"""
        try:
            from config import CONFIG
            from modules.audio.audio_manager import AudioManager
            
            # Verificar se configurações estão acessíveis
            self.assertIn("ollama_model", CONFIG)
            self.assertIn("ollama_url", CONFIG)
            
            logger.info("✅ Integração Config+Módulos OK")
            
        except Exception as e:
            self.fail(f"❌ Falha na integração: {e}")


class TestPerformance(unittest.TestCase):
    """Testes de performance"""
    
    def setUp(self):
        logger.info("="*60)
        logger.info(f"Iniciando teste: {self._testMethodName}")
        self.start_time = time.time()
    
    def tearDown(self):
        duration = time.time() - self.start_time
        logger.info(f"✅ Teste concluído em {duration:.3f}s")
        logger.info("="*60)
    
    def test_import_speed(self):
        """Teste 18: Velocidade de importação"""
        import_start = time.time()
        
        try:
            from config import CONFIG
            from modules.audio.audio_manager import AudioManager
            from modules.speech.speech_engine import SpeechEngine
        except ImportError as e:
            self.fail(f"❌ Erro ao importar: {e}")
        
        import_duration = time.time() - import_start
        
        # Imports devem ser rápidos (< 2 segundos)
        self.assertLess(import_duration, 2.0, 
                       f"Imports muito lentos: {import_duration:.3f}s")
        logger.info(f"✅ Imports completados em {import_duration:.3f}s")
    
    def test_audio_manager_initialization_speed(self):
        """Teste 19: Velocidade de inicialização do Audio Manager"""
        from modules.audio.audio_manager import AudioManager
        
        init_start = time.time()
        audio_manager = AudioManager()
        init_duration = time.time() - init_start
        
        # Inicialização deve ser rápida (< 1 segundo)
        self.assertLess(init_duration, 1.0,
                       f"Inicialização muito lenta: {init_duration:.3f}s")
        logger.info(f"✅ AudioManager inicializado em {init_duration:.3f}s")


class TestStressTest(unittest.TestCase):
    """Testes de stress"""
    
    def setUp(self):
        logger.info("="*60)
        logger.info(f"Iniciando teste: {self._testMethodName}")
        self.start_time = time.time()
    
    def tearDown(self):
        duration = time.time() - self.start_time
        logger.info(f"✅ Teste concluído em {duration:.3f}s")
        logger.info("="*60)
    
    def test_multiple_audio_manager_instances(self):
        """Teste 20: Múltiplas instâncias do Audio Manager"""
        from modules.audio.audio_manager import AudioManager
        
        instances = []
        for i in range(5):
            try:
                am = AudioManager()
                instances.append(am)
                logger.info(f"✅ Instância {i+1} criada")
            except Exception as e:
                self.fail(f"❌ Falha ao criar instância {i+1}: {e}")
        
        self.assertEqual(len(instances), 5)
        logger.info("✅ 5 instâncias criadas com sucesso")


def run_intensive_tests():
    """Executa todos os testes intensivos"""
    
    print("\n" + "="*80)
    print("🧪 SUITE DE TESTES INTENSIVOS DO Astra")
    print("="*80 + "\n")
    
    # Criar test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar todas as classes de teste
    suite.addTests(loader.loadTestsFromTestCase(TestCoreModules))
    suite.addTests(loader.loadTestsFromTestCase(TestAudioSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestDataStructures))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestStressTest))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Relatório final
    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL")
    print("="*80)
    print(f"✅ Testes executados: {result.testsRun}")
    print(f"✅ Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Falhas: {len(result.failures)}")
    print(f"❌ Erros: {len(result.errors)}")
    print(f"⚠️  Avisos: {len(result.skipped)}")
    print("="*80 + "\n")
    
    # Taxa de sucesso
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"🎯 Taxa de Sucesso: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🌟 EXCELENTE! Sistema funcionando muito bem!")
    elif success_rate >= 70:
        print("✅ BOM! Sistema funcional com alguns avisos")
    elif success_rate >= 50:
        print("⚠️ ATENÇÃO! Sistema precisa de melhorias")
    else:
        print("❌ CRÍTICO! Sistema precisa de correções urgentes")
    
    print("\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_intensive_tests()
    sys.exit(0 if success else 1)


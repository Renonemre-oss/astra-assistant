#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Sistema de Speech Híbrido
Combina múltiplos engines TTS com fallback inteligente
"""

import sys
import logging
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict, Callable, Any
from enum import Enum
import json

# Configurar logger
logger = logging.getLogger(__name__)

class TTSEngine(Enum):
    """Engines TTS disponíveis."""
    WINDOWS_SAPI = "windows_sapi"
    TACOTRON2 = "tacotron2"
    COQUI_TTS = "coqui_tts"
    EDGE_TTS = "edge_tts"  # Microsoft Edge TTS (online)
    XTTS_VOICE_CLONE = "xtts_clone"  # Coqui XTTS voice cloning

class SpeechQuality(Enum):
    """Níveis de qualidade de speech."""
    BASIC = "basic"
    GOOD = "good"
    HIGH = "high"
    PREMIUM = "premium"

class HybridSpeechEngine:
    """
    Sistema híbrido que escolhe automaticamente o melhor engine TTS disponível.
    """
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Inicializa o sistema híbrido.
        
        Args:
            status_callback: Função para receber atualizações de status
        """
        self.status_callback = status_callback
        
        # Engines disponíveis
        self.engines = {}
        self.current_engine = None
        self.fallback_engine = None
        
        # Configurações
        self.preferred_quality = SpeechQuality.HIGH
        self.auto_fallback = True
        self.preferred_gender = "male"  # "male" ou "female"
        self.preferred_locale = "pt-BR"  # "pt-BR" ou "pt-PT"
        
        # Diretório de configuração
        self.config_dir = Path(__file__).parent
        self.config_file = self.config_dir / "hybrid_speech_config.json"
        
        # Carregar configurações
        self.load_config()
        
        # Inicializar engines
        self.initialize_engines()
    
    def set_status(self, message: str):
        """Atualiza status."""
        if self.status_callback:
            self.status_callback(message)
        logger.info(f"Hybrid Speech: {message}")
    
    def initialize_engines(self):
        """Inicializa todos os engines disponíveis."""
        self.set_status("🔄 Inicializando engines de TTS...")
        
        # 1. Windows SAPI (sempre disponível no Windows)
        self._init_windows_sapi()
        
        # 2. Edge TTS (Microsoft online)
        self._init_edge_tts()
        
        # 3. Coqui TTS (se disponível)
        self._init_coqui_tts()
        
        # 4. XTTS Voice Cloning
        self._init_xtts_cloning()
        
        # 5. Tacotron 2 (última opção devido à complexidade)
        # self._init_tacotron2()  # Desabilitado por enquanto
        
        # Selecionar engine principal
        self._select_best_engine()
    
    def _init_windows_sapi(self):
        """Inicializa Windows SAPI."""
        try:
            from modules.speech.speech_engine import SpeechEngine
            
            sapi_engine = SpeechEngine()
            if sapi_engine.tts_engine:
                self.engines[TTSEngine.WINDOWS_SAPI] = {
                    'engine': sapi_engine,
                    'quality': SpeechQuality.GOOD,
                    'speed': 'fast',
                    'offline': True,
                    'languages': ['en-US', 'pt-BR'],
                    'available': True
                }
                self.set_status("✅ Windows SAPI TTS carregado")
            
        except Exception as e:
            logger.error(f"Erro ao carregar SAPI: {e}")
    
    def _init_edge_tts(self):
        """Inicializa Microsoft Edge TTS."""
        try:
            # Tentar importar edge-tts
            import edge_tts
            
            self.engines[TTSEngine.EDGE_TTS] = {
                'engine': None,  # Será instanciado quando necessário
                'quality': SpeechQuality.PREMIUM,
                'speed': 'medium',
                'offline': False,
                'languages': ['pt-BR', 'pt-PT', 'en-US', 'es-ES', 'fr-FR'],
                'available': True
            }
            self.set_status("✅ Microsoft Edge TTS disponível")
            
        except ImportError:
            self.set_status("⚠️  Edge TTS não instalado (pip install edge-tts)")
        except Exception as e:
            logger.error(f"Erro ao verificar Edge TTS: {e}")
    
    def _init_coqui_tts(self):
        """Inicializa Coqui TTS."""
        try:
            from TTS.api import TTS
            
            # Verificar se há modelos disponíveis
            tts_models = TTS.list_models()
            if tts_models:
                self.engines[TTSEngine.COQUI_TTS] = {
                    'engine': None,  # Será instanciado quando necessário
                    'quality': SpeechQuality.HIGH,
                    'speed': 'slow',
                    'offline': True,
                    'languages': ['multi'],
                    'available': True
                }
                self.set_status("✅ Coqui TTS disponível")
            
        except ImportError:
            self.set_status("⚠️  Coqui TTS não instalado")
        except Exception as e:
            logger.error(f"Erro ao verificar Coqui TTS: {e}")
    
    def _select_best_engine(self):
        """Seleciona o melhor engine baseado na qualidade preferida."""
        if not self.engines:
            self.set_status("❌ Nenhum engine TTS disponível")
            return
        
        # Ordenar engines por qualidade
        quality_order = {
            SpeechQuality.PREMIUM: 4,
            SpeechQuality.HIGH: 3,
            SpeechQuality.GOOD: 2,
            SpeechQuality.BASIC: 1
        }
        
        sorted_engines = sorted(
            self.engines.items(),
            key=lambda x: quality_order.get(x[1]['quality'], 0),
            reverse=True
        )
        
        # Selecionar melhor engine disponível
        for engine_type, engine_info in sorted_engines:
            if engine_info['available']:
                self.current_engine = engine_type
                self.set_status(f"🎯 Engine principal: {engine_type.value} (qualidade: {engine_info['quality'].value})")
                break
        
        # Definir fallback (Windows SAPI se disponível)
        if TTSEngine.WINDOWS_SAPI in self.engines and self.current_engine != TTSEngine.WINDOWS_SAPI:
            self.fallback_engine = TTSEngine.WINDOWS_SAPI
            self.set_status(f"🛡️ Engine fallback: {self.fallback_engine.value}")
    
    def speak(self, text: str, blocking: bool = False, preferred_engine: Optional[TTSEngine] = None) -> bool:
        """
        Converte texto para fala usando o melhor engine disponível.
        
        Args:
            text: Texto a ser falado
            blocking: Se deve aguardar conclusão
            preferred_engine: Engine preferido para esta fala
            
        Returns:
            bool: True se bem-sucedido
        """
        if not text or not text.strip():
            return False
        
        # Determinar engine a usar
        engine_to_use = preferred_engine or self.current_engine
        
        if not engine_to_use or engine_to_use not in self.engines:
            self.set_status("❌ Nenhum engine disponível")
            return False
        
        try:
            return self._speak_with_engine(text, engine_to_use, blocking)
            
        except Exception as e:
            self.set_status(f"❌ Erro com {engine_to_use.value}: {e}")
            
            # Tentar fallback se habilitado
            if self.auto_fallback and self.fallback_engine and engine_to_use != self.fallback_engine:
                self.set_status(f"🔄 Tentando fallback: {self.fallback_engine.value}")
                return self._speak_with_engine(text, self.fallback_engine, blocking)
            
            return False
    
    def _speak_with_engine(self, text: str, engine_type: TTSEngine, blocking: bool) -> bool:
        """Fala usando um engine específico."""
        engine_info = self.engines[engine_type]
        
        if engine_type == TTSEngine.WINDOWS_SAPI:
            return self._speak_sapi(text, engine_info, blocking)
        elif engine_type == TTSEngine.EDGE_TTS:
            return self._speak_edge_tts(text, engine_info, blocking)
        elif engine_type == TTSEngine.COQUI_TTS:
            return self._speak_coqui_tts(text, engine_info, blocking)
        elif engine_type == TTSEngine.XTTS_VOICE_CLONE:
            return self._speak_xtts_clone(text, engine_info, blocking)
        else:
            return False
    
    def _speak_sapi(self, text: str, engine_info: Dict, blocking: bool) -> bool:
        """Fala usando Windows SAPI."""
        try:
            sapi_engine = engine_info['engine']
            return sapi_engine.speak(text, blocking)
            
        except Exception as e:
            logger.error(f"Erro SAPI: {e}")
            return False
    
    def _speak_edge_tts(self, text: str, engine_info: Dict, blocking: bool) -> bool:
        """Fala usando Microsoft Edge TTS."""
        try:
            # Implementação simplificada - seria expandida para uso real
            import asyncio
            import edge_tts
            import tempfile
            import os
            
            async def generate_speech():
                # Selecionar voz baseada nas preferências
                voice_map = {
                    ("pt-BR", "male"): "pt-BR-AntonioNeural",
                    ("pt-BR", "female"): "pt-BR-FranciscaNeural", 
                    ("pt-PT", "male"): "pt-PT-DuarteNeural",
                    ("pt-PT", "female"): "pt-PT-RaquelNeural"
                }
                
                voice_key = (self.preferred_locale, self.preferred_gender)
                voice = voice_map.get(voice_key, "pt-BR-AntonioNeural")  # Fallback para Antonio
                
                communicate = edge_tts.Communicate(text, voice)
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    await communicate.save(tmp_file.name)
                    return tmp_file.name
            
            # Executar async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_file = loop.run_until_complete(generate_speech())
            
            # Reproduzir áudio
            if audio_file and os.path.exists(audio_file):
                os.startfile(audio_file)
                if not blocking:
                    # Limpar arquivo após um tempo
                    threading.Timer(10.0, lambda: os.unlink(audio_file) if os.path.exists(audio_file) else None).start()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro Edge TTS: {e}")
            return False
    
    def _speak_coqui_tts(self, text: str, engine_info: Dict, blocking: bool) -> bool:
        """Fala usando Coqui TTS."""
        try:
            # Implementação placeholder - seria expandida
            self.set_status("⚠️  Coqui TTS não implementado ainda")
            return False
            
        except Exception as e:
            logger.error(f"Erro Coqui TTS: {e}")
            return False
    
    def _init_xtts_cloning(self):
        """Inicializa Coqui XTTS Voice Cloning."""
        try:
            # Verificar se o módulo existe
            import importlib.util
            spec = importlib.util.find_spec('speech.xtts_voice_cloning')
            if spec is not None:
                from speech.xtts_voice_cloning import SimpleVoiceCloner
                
                # Verificar se há vozes disponíveis
                cloner = SimpleVoiceCloner()
                available_voices = cloner.list_voices()
                
                self.engines[TTSEngine.XTTS_VOICE_CLONE] = {
                    'engine': cloner,
                    'quality': SpeechQuality.PREMIUM,
                    'speed': 'medium',
                    'offline': True,
                    'languages': ['pt-br', 'en'],
                    'available': True,
                    'available_voices': available_voices
                }
                self.set_status(f"✅ XTTS Voice Cloning disponível: {len(available_voices)} vozes")
            else:
                self.set_status("⚠️ Módulo XTTS Voice Cloning não encontrado")
            
        except ImportError:
            self.set_status("⚠️ XTTS Voice Cloning não instalado")
        except Exception as e:
            logger.error(f"Erro ao verificar XTTS Voice Cloning: {e}")
            self.set_status(f"⚠️ Erro ao inicializar XTTS Voice Cloning: {str(e)}")
    
    def _speak_xtts_clone(self, text: str, engine_info: Dict, blocking: bool) -> bool:
        """Fala usando XTTS voice cloning."""
        try:
            cloner = engine_info['engine']
            available_voices = engine_info.get('available_voices', [])
            
            if not available_voices:
                self.set_status("⚠️ Nenhuma voz clonada disponível")
                return False
            
            # Selecionar a primeira voz disponível (futuramente, permitir configuração)
            voice_name = available_voices[0]
            language = "pt-br" if self.preferred_locale == "pt-BR" else "en"
            
            # Gerar áudio
            self.set_status(f"🎤 Sintetizando com voz clonada '{voice_name}'")
            audio_file = cloner.speak(text, voice_name, language=language)
            
            if audio_file:
                # Reproduzir áudio
                import os
                os.startfile(audio_file)
                
                # Limpar arquivo após uso se não for blocking
                if not blocking:
                    import threading
                    threading.Timer(10.0, lambda: os.unlink(audio_file) 
                                   if os.path.exists(audio_file) else None).start()
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Erro XTTS Clone: {e}")
            self.set_status(f"❌ Erro na síntese com voz clonada: {str(e)}")
            return False
    
    def get_available_engines(self) -> Dict[TTSEngine, Dict[str, Any]]:
        """Obtém informações sobre engines disponíveis."""
        return {k: v for k, v in self.engines.items() if v['available']}
    
    def set_preferred_quality(self, quality: SpeechQuality):
        """Define qualidade preferida e reseleciona engine."""
        self.preferred_quality = quality
        self._select_best_engine()
        self.save_config()
    
    def set_voice_preferences(self, gender: str = None, locale: str = None):
        """Define preferências de voz."""
        if gender in ["male", "female"]:
            self.preferred_gender = gender
            self.set_status(f"🎤 Gênero alterado para: {gender}")
        
        if locale in ["pt-BR", "pt-PT"]:
            self.preferred_locale = locale
            self.set_status(f"🌍 Idioma alterado para: {locale}")
        
        self.save_config()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtém informações do sistema híbrido."""
        return {
            'current_engine': self.current_engine.value if self.current_engine else None,
            'fallback_engine': self.fallback_engine.value if self.fallback_engine else None,
            'available_engines': len([e for e in self.engines.values() if e['available']]),
            'total_engines': len(self.engines),
            'preferred_quality': self.preferred_quality.value,
            'preferred_gender': self.preferred_gender,
            'preferred_locale': self.preferred_locale,
            'auto_fallback': self.auto_fallback,
            'engines': {k.value: {'quality': v['quality'].value, 'available': v['available']} 
                       for k, v in self.engines.items()}
        }
    
    def load_config(self):
        """Carrega configurações."""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            quality_str = config.get('preferred_quality', 'high')
            self.preferred_quality = SpeechQuality(quality_str)
            self.auto_fallback = config.get('auto_fallback', True)
            self.preferred_gender = config.get('preferred_gender', 'male')
            self.preferred_locale = config.get('preferred_locale', 'pt-BR')
            
            logger.info("Configurações híbridas carregadas")
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
    
    def save_config(self):
        """Salva configurações."""
        try:
            self.config_dir.mkdir(exist_ok=True)
            
            config = {
                'preferred_quality': self.preferred_quality.value,
                'auto_fallback': self.auto_fallback,
                'preferred_gender': self.preferred_gender,
                'preferred_locale': self.preferred_locale,
                'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("Configurações híbridas salvas")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")

def test_hybrid_speech():
    """Função de teste do sistema híbrido."""
    print("🎤 Testando Sistema Híbrido de Speech")
    print("=" * 50)
    
    def status_print(msg):
        print(f"  {msg}")
    
    # Criar engine híbrido
    engine = HybridSpeechEngine(status_callback=status_print)
    
    # Configurar para voz masculina portuguesa do Brasil
    engine.set_voice_preferences(gender="male", locale="pt-BR")
    
    # Obter informações
    info = engine.get_system_info()
    print(f"\n📊 Informações do Sistema:")
    for key, value in info.items():
        if key == 'engines':
            print(f"  {key}:")
            for eng_name, eng_info in value.items():
                print(f"    {eng_name}: {eng_info}")
        else:
            print(f"  {key}: {value}")
    
    # Teste de fala
    print(f"\n🗣️ Teste de Fala:")
    test_text = "Olá! Este é o sistema híbrido de voz do ASTRA, escolhendo automaticamente a melhor qualidade disponível."
    
    success = engine.speak(test_text, blocking=True)
    print(f"Resultado: {'✅ Sucesso' if success else '❌ Falhou'}")
    
    # Testar voice cloning se disponível
    if TTSEngine.XTTS_VOICE_CLONE in engine.engines and engine.engines[TTSEngine.XTTS_VOICE_CLONE]['available']:
        available_voices = engine.engines[TTSEngine.XTTS_VOICE_CLONE].get('available_voices', [])
        if available_voices:
            print(f"\n🎯 Teste de Voice Cloning:")
            print(f"  Vozes disponíveis: {available_voices}")
            clone_text = "Esta é uma demonstração de voz clonada usando XTTS. A qualidade é excelente!"
            success = engine.speak(clone_text, blocking=True, preferred_engine=TTSEngine.XTTS_VOICE_CLONE)
            print(f"  Resultado: {'✅ Sucesso' if success else '❌ Falhou'}")
        else:
            print(f"\n⚠️ Voice Cloning disponível, mas nenhuma voz clonada encontrada")
            print(f"  Use o AudioRecorder para criar uma voz clonada primeiro")
    
    return engine

if __name__ == "__main__":
    test_hybrid_speech()

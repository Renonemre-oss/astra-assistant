#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Sistema de Voz Limpo e Moderno
Sistema de speech (TTS + STT) redesenhado do zero para máxima simplicidade e confiabilidade
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

class EngineType(Enum):
    """Tipos de engines de TTS disponíveis."""
    WINDOWS_SAPI = "windows_sapi"
    SYSTEM_DEFAULT = "system_default"
    OFFLINE = "offline"

class SpeechStatus(Enum):
    """Estados do sistema de speech."""
    READY = "ready"
    SPEAKING = "speaking" 
    LISTENING = "listening"
    PROCESSING = "processing"
    ERROR = "error"

class SpeechEngine:
    """
    Sistema de speech principal do ASTRA.
    Focado em simplicidade, confiabilidade e performance.
    """
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Inicializa o sistema de speech.
        
        Args:
            status_callback: Função para receber atualizações de status
        """
        self.status_callback = status_callback
        self.status = SpeechStatus.READY
        
        # Engines disponíveis
        self.tts_engine = None
        self.stt_engine = None
        self.current_engine_type = None
        
        # Configurações
        self.voice_rate = 180  # Velocidade de fala (palavras por minuto)
        self.voice_volume = 0.9  # Volume (0.0 - 1.0)
        self.voice_index = 0  # Índice da voz atual
        
        # Controle de threads
        self.is_speaking = False
        self.speech_thread = None
        
        # Diretório de configuração
        self.config_dir = Path(__file__).parent
        self.config_file = self.config_dir / "speech_config.json"
        
        # Carregar configurações
        self.load_config()
        
        # Inicializar engine padrão
        self.initialize_default_engine()
    
    def set_status(self, message: str, status: SpeechStatus = None):
        """Atualiza status do sistema."""
        if status:
            self.status = status
            
        if self.status_callback:
            self.status_callback(f"[{self.status.value.upper()}] {message}")
            
        logger.info(f"Speech Engine: {message}")
    
    def initialize_default_engine(self) -> bool:
        """Inicializa o engine padrão (Windows SAPI)."""
        self.set_status("🔄 Inicializando sistema de speech...", SpeechStatus.PROCESSING)
        
        # Tentar Windows SAPI primeiro (mais confiável)
        if self._init_windows_sapi():
            self.current_engine_type = EngineType.WINDOWS_SAPI
            self.set_status("✅ Windows SAPI TTS carregado", SpeechStatus.READY)
            return True
        
        # Fallback para sistema padrão
        if self._init_system_default():
            self.current_engine_type = EngineType.SYSTEM_DEFAULT
            self.set_status("✅ Sistema TTS padrão carregado", SpeechStatus.READY)
            return True
        
        self.set_status("❌ Nenhum sistema TTS disponível", SpeechStatus.ERROR)
        return False
    
    def _init_windows_sapi(self) -> bool:
        """Inicializa Windows SAPI TTS."""
        try:
            import pyttsx3
            
            self.tts_engine = pyttsx3.init(driverName='sapi5')
            
            if not self.tts_engine:
                return False
            
            # Configurar propriedades básicas
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            
            # Selecionar voz
            voices = self.tts_engine.getProperty('voices')
            if voices and len(voices) > self.voice_index:
                self.tts_engine.setProperty('voice', voices[self.voice_index].id)
            
            logger.info(f"Windows SAPI TTS inicializado com {len(voices)} vozes")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Windows SAPI: {e}")
            return False
    
    def _init_system_default(self) -> bool:
        """Inicializa TTS padrão do sistema."""
        try:
            import pyttsx3
            
            self.tts_engine = pyttsx3.init()
            
            if not self.tts_engine:
                return False
            
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            
            logger.info("Sistema TTS padrão inicializado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar TTS padrão: {e}")
            return False
    
    def speak(self, text: str, blocking: bool = False) -> bool:
        """
        Converte texto para fala.
        
        Args:
            text: Texto a ser falado
            blocking: Se deve aguardar conclusão da fala
            
        Returns:
            bool: True se iniciou com sucesso
        """
        if not text or not text.strip():
            return False
        
        if not self.tts_engine:
            self.set_status("❌ Engine TTS não disponível", SpeechStatus.ERROR)
            return False
        
        # Limpar texto
        clean_text = self._clean_text(text)
        if not clean_text:
            return False
        
        try:
            if blocking:
                return self._speak_blocking(clean_text)
            else:
                return self._speak_async(clean_text)
                
        except Exception as e:
            self.set_status(f"❌ Erro na síntese de fala: {e}", SpeechStatus.ERROR)
            logger.error(f"Erro na síntese: {e}")
            return False
    
    def _clean_text(self, text: str) -> str:
        """Limpa e prepara texto para TTS."""
        import re
        
        # Remover caracteres problemáticos
        text = re.sub(r'[^\w\s\.,!?;:\-\(\)]', ' ', text)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text)
        
        # Limitar tamanho
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text.strip()
    
    def _speak_blocking(self, text: str) -> bool:
        """Fala texto de forma síncrona."""
        try:
            self.is_speaking = True
            self.set_status(f"🗣️ Falando: {text[:50]}...", SpeechStatus.SPEAKING)
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na fala síncrona: {e}")
            return False
        finally:
            self.is_speaking = False
            self.set_status("✅ Fala concluída", SpeechStatus.READY)
    
    def _speak_async(self, text: str) -> bool:
        """Fala texto de forma assíncrona."""
        if self.is_speaking:
            self.stop_speaking()
        
        def speak_thread():
            self._speak_blocking(text)
        
        try:
            self.speech_thread = threading.Thread(target=speak_thread, daemon=True)
            self.speech_thread.start()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar thread de fala: {e}")
            return False
    
    def stop_speaking(self):
        """Para a fala atual."""
        try:
            if self.tts_engine and self.is_speaking:
                self.tts_engine.stop()
                self.set_status("🚫 Fala interrompida", SpeechStatus.READY)
                
            self.is_speaking = False
            
        except Exception as e:
            logger.error(f"Erro ao parar fala: {e}")
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Obtém lista de vozes disponíveis."""
        voices_info = []
        
        if not self.tts_engine:
            return voices_info
        
        try:
            voices = self.tts_engine.getProperty('voices')
            
            for i, voice in enumerate(voices):
                voices_info.append({
                    'index': i,
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown')
                })
                
        except Exception as e:
            logger.error(f"Erro ao obter vozes: {e}")
        
        return voices_info
    
    def set_voice(self, voice_index: int) -> bool:
        """
        Define a voz a ser usada.
        
        Args:
            voice_index: Índice da voz na lista de vozes disponíveis
            
        Returns:
            bool: True se alterada com sucesso
        """
        if not self.tts_engine:
            return False
        
        try:
            voices = self.tts_engine.getProperty('voices')
            
            if 0 <= voice_index < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_index].id)
                self.voice_index = voice_index
                self.save_config()
                
                self.set_status(f"🎵 Voz alterada: {voices[voice_index].name}")
                return True
            else:
                logger.error(f"Índice de voz inválido: {voice_index}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao alterar voz: {e}")
            return False
    
    def set_rate(self, rate: int) -> bool:
        """
        Define velocidade de fala.
        
        Args:
            rate: Velocidade em palavras por minuto (100-300)
            
        Returns:
            bool: True se alterada com sucesso
        """
        if not self.tts_engine:
            return False
        
        try:
            # Limitar valores
            rate = max(100, min(300, rate))
            
            self.tts_engine.setProperty('rate', rate)
            self.voice_rate = rate
            self.save_config()
            
            self.set_status(f"⚡ Velocidade alterada: {rate} WPM")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar velocidade: {e}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """
        Define volume de fala.
        
        Args:
            volume: Volume de 0.0 a 1.0
            
        Returns:
            bool: True se alterado com sucesso
        """
        if not self.tts_engine:
            return False
        
        try:
            # Limitar valores
            volume = max(0.0, min(1.0, volume))
            
            self.tts_engine.setProperty('volume', volume)
            self.voice_volume = volume
            self.save_config()
            
            self.set_status(f"🔊 Volume alterado: {int(volume * 100)}%")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao alterar volume: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtém informações do sistema de speech."""
        voices = self.get_available_voices()
        
        return {
            'engine_type': self.current_engine_type.value if self.current_engine_type else None,
            'status': self.status.value,
            'is_speaking': self.is_speaking,
            'voice_count': len(voices),
            'current_voice': self.voice_index,
            'voice_rate': self.voice_rate,
            'voice_volume': self.voice_volume,
            'tts_available': self.tts_engine is not None,
            'stt_available': self.stt_engine is not None
        }
    
    def load_config(self):
        """Carrega configurações do arquivo JSON."""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.voice_rate = config.get('voice_rate', 180)
            self.voice_volume = config.get('voice_volume', 0.9)
            self.voice_index = config.get('voice_index', 0)
            
            logger.info("Configurações de speech carregadas")
            
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {e}")
    
    def save_config(self):
        """Salva configurações no arquivo JSON."""
        try:
            self.config_dir.mkdir(exist_ok=True)
            
            config = {
                'voice_rate': self.voice_rate,
                'voice_volume': self.voice_volume,
                'voice_index': self.voice_index,
                'engine_type': self.current_engine_type.value if self.current_engine_type else None,
                'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("Configurações de speech salvas")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")

# Instância global
_speech_engine: Optional[SpeechEngine] = None

def get_speech_engine() -> SpeechEngine:
    """Obtém instância global do sistema de speech."""
    global _speech_engine
    if _speech_engine is None:
        _speech_engine = SpeechEngine()
    return _speech_engine

def speak(text: str, blocking: bool = False) -> bool:
    """Função de conveniência para falar texto."""
    return get_speech_engine().speak(text, blocking)

def stop_speaking():
    """Função de conveniência para parar fala."""
    get_speech_engine().stop_speaking()

def test_speech_engine():
    """Função de teste do sistema de speech."""
    print("🎤 Testando Sistema de Speech do ASTRA")
    print("=" * 45)
    
    def status_print(msg):
        print(f"  {msg}")
    
    # Criar instância
    engine = SpeechEngine(status_callback=status_print)
    
    # Obter informações
    info = engine.get_system_info()
    print(f"\n📊 Informações do Sistema:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Listar vozes
    voices = engine.get_available_voices()
    print(f"\n🎵 Vozes disponíveis ({len(voices)}):")
    for voice in voices[:5]:  # Mostrar apenas as primeiras 5
        print(f"  {voice['index']}: {voice['name']}")
    
    # Teste de fala
    print(f"\n🗣️ Teste de fala:")
    success = engine.speak("Olá! Este é o novo sistema de voz do ASTRA, funcionando perfeitamente.", blocking=True)
    print(f"Resultado: {'✅ Sucesso' if success else '❌ Falhou'}")
    
    return engine

if __name__ == "__main__":
    test_speech_engine()

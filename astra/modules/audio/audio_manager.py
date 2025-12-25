#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Audio Manager
Manages text-to-speech and audio functionality for the assistant
Wraps the SpeechEngine to provide a consistent audio interface
"""

import logging
import threading
import time
from typing import Optional, Callable
from pathlib import Path

# Import error handling system
from utils.error_handler import handle_errors, ErrorLevel, ErrorCategory

# Import the SpeechEngine
from modules.speech.speech_engine import SpeechEngine, SpeechStatus

# Configure logger
logger = logging.getLogger(__name__)

# Dependencies for testing framework
DEPENDENCIES = {
    'speech_engine': 'speech.speech_engine.SpeechEngine',
    'error_handler': 'utils.error_handler',
    'logging': 'logging',
    'threading': 'threading',
    'pathlib': 'pathlib.Path'
}


class AudioManager:
    """
    Audio Manager for ASTRA Assistant.
    Provides text-to-speech functionality using the SpeechEngine.
    """
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the Audio Manager.
        
        Args:
            status_callback: Function to receive status updates
        """
        self.status_callback = status_callback
        self.speech_engine = None
        self.tts_loaded = False
        self._shutdown = False
        
        # Initialize in a separate thread to avoid blocking
        self._init_thread = None
        
        logger.info("Audio Manager initialized")
        self._set_status("🔄 Audio Manager inicializado")
    
    def _set_status(self, message: str):
        """Send status update to callback."""
        if self.status_callback:
            self.status_callback(message)
        logger.info(f"AudioManager: {message}")
    
    @handle_errors(level=ErrorLevel.HIGH, category=ErrorCategory.SYSTEM, 
                   user_message="Falha ao carregar sistema de voz")
    def load_tts_model(self):
        """
        Load the TTS model in a background thread.
        This is called by the assistant to initialize TTS.
        """
        if self.tts_loaded:
            return
            
        def load_thread():
            try:
                self._set_status("🔄 Carregando modelo TTS...")
                
                # Create speech engine with our status callback
                self.speech_engine = SpeechEngine(status_callback=self._set_status)
                
                if self.speech_engine.tts_engine:
                    self.tts_loaded = True
                    self._set_status("✅ Modelo TTS carregado com sucesso")
                else:
                    self.tts_loaded = False
                    self._set_status("⚠️ TTS não disponível - modo texto")
                    
            except Exception as e:
                logger.error(f"Erro ao carregar modelo TTS: {e}")
                self._set_status("❌ Erro ao carregar TTS")
                self.tts_loaded = False
                raise  # Re-raise for error handler
        
        # Start loading in background
        self._init_thread = threading.Thread(target=load_thread, daemon=True)
        self._init_thread.start()
    
    @handle_errors(level=ErrorLevel.MEDIUM, category=ErrorCategory.SYSTEM, 
                   user_message="Falha na síntese de voz", raise_on_error=False)
    def text_to_speech(self, text: str) -> bool:
        """
        Convert text to speech.
        
        Args:
            text: Text to be spoken
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self._shutdown:
            return False
            
        if not text or not text.strip():
            return False
        
        # If TTS is not loaded, just log and return
        if not self.tts_loaded or not self.speech_engine:
            logger.info(f"TTS não disponível. Texto: {text[:100]}...")
            return False
        
        # Use the speech engine to speak (async by default)
        success = self.speech_engine.speak(text, blocking=False)
        
        if success:
            logger.info(f"TTS iniciado: {text[:50]}...")
        else:
            logger.warning("Falha ao iniciar TTS")
            
        return success
    
    def stop_speech(self):
        """Stop current speech."""
        if self.speech_engine:
            try:
                self.speech_engine.stop_speaking()
                logger.info("Fala interrompida")
            except Exception as e:
                logger.error(f"Erro ao parar fala: {e}")
    
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        if self.speech_engine:
            return self.speech_engine.is_speaking
        return False
    
    def get_status(self) -> dict:
        """Get current audio manager status."""
        if self.speech_engine:
            engine_info = self.speech_engine.get_system_info()
        else:
            engine_info = {}
            
        return {
            'tts_loaded': self.tts_loaded,
            'is_speaking': self.is_speaking(),
            'shutdown': self._shutdown,
            'engine_info': engine_info
        }
    
    def set_voice_settings(self, rate: Optional[int] = None, 
                          volume: Optional[float] = None, 
                          voice_index: Optional[int] = None) -> bool:
        """
        Configure voice settings.
        
        Args:
            rate: Speech rate in words per minute (100-300)
            volume: Volume level (0.0-1.0)
            voice_index: Index of voice to use
            
        Returns:
            bool: True if settings were applied successfully
        """
        if not self.speech_engine:
            return False
            
        success = True
        
        try:
            if rate is not None:
                success &= self.speech_engine.set_rate(rate)
                
            if volume is not None:
                success &= self.speech_engine.set_volume(volume)
                
            if voice_index is not None:
                success &= self.speech_engine.set_voice(voice_index)
                
        except Exception as e:
            logger.error(f"Erro ao configurar voz: {e}")
            return False
            
        return success
    
    def get_available_voices(self) -> list:
        """Get list of available voices."""
        if self.speech_engine:
            return self.speech_engine.get_available_voices()
        return []
    
    def shutdown(self):
        """Shutdown the audio manager and cleanup resources."""
        self._shutdown = True
        
        try:
            # Stop any ongoing speech
            if self.speech_engine:
                self.speech_engine.stop_speaking()
                
            # Wait for init thread to finish
            if self._init_thread and self._init_thread.is_alive():
                self._init_thread.join(timeout=2.0)
                
            self._set_status("🔐 Audio Manager desligado")
            logger.info("Audio Manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Erro no shutdown do Audio Manager: {e}")


# Factory function for convenience
def create_audio_manager(status_callback: Optional[Callable[[str], None]] = None) -> AudioManager:
    """Create and return a new AudioManager instance."""
    return AudioManager(status_callback=status_callback)


def test_audio_manager():
    """Test the AudioManager functionality."""
    print("🎤 Testando Audio Manager")
    print("=" * 30)
    
    def status_print(msg):
        print(f"Status: {msg}")
    
    # Create audio manager
    audio_mgr = AudioManager(status_callback=status_print)
    
    # Load TTS model
    print("\n1. Carregando TTS...")
    audio_mgr.load_tts_model()
    
    # Wait a bit for loading
    time.sleep(3)
    
    # Check status
    print("\n2. Status do sistema:")
    status = audio_mgr.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test speech
    if audio_mgr.tts_loaded:
        print("\n3. Testando fala...")
        success = audio_mgr.text_to_speech("Olá! Este é o Audio Manager do ASTRA funcionando perfeitamente.")
        print(f"Resultado: {'✅ Sucesso' if success else '❌ Falhou'}")
        
        # Wait for speech to complete
        time.sleep(5)
    else:
        print("\n3. TTS não disponível para teste")
    
    # Shutdown
    print("\n4. Fazendo shutdown...")
    audio_mgr.shutdown()
    
    return audio_mgr


if __name__ == "__main__":
    test_audio_manager()

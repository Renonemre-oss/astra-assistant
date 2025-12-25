#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA TTS - Sistema de Voz Simplificado
Combina Piper TTS (preferido) com pyttsx3 (fallback) de forma elegante.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    logger.warning("Piper TTS não disponível")


class AstraTTS:
    """
    Sistema de TTS do Astra com Piper neural e fallback para pyttsx3.
    """
    
    def __init__(self, use_piper: bool = True):
        """
        Inicializa o sistema de TTS.
        
        Args:
            use_piper: Se True, tenta usar Piper. Se False, usa apenas pyttsx3.
        """
        self.piper_voice = None
        self.pyttsx3_engine = None
        self.current_engine = None
        
        # Tentar inicializar Piper primeiro
        if use_piper and PIPER_AVAILABLE:
            self._init_piper()
        
        # Fallback para pyttsx3
        if not self.piper_voice:
            self._init_pyttsx3()
    
    def _init_piper(self) -> bool:
        """Inicializa Piper TTS com modelo português."""
        try:
            # Procurar modelo na pasta padrão
            models_dir = Path(__file__).parent / "piper_models"
            
            # Procurar primeiro modelo .onnx disponível
            model_files = list(models_dir.glob("*.onnx"))
            
            if not model_files:
                logger.warning("Nenhum modelo Piper encontrado")
                return False
            
            model_path = model_files[0]
            logger.info(f"Carregando modelo Piper: {model_path.name}")
            
            # Carregar modelo
            self.piper_voice = PiperVoice.load(str(model_path))
            self.current_engine = "piper"
            
            logger.info(f"✅ Piper TTS inicializado: {model_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Piper: {e}")
            return False
    
    def _init_pyttsx3(self) -> bool:
        """Inicializa pyttsx3 como fallback."""
        try:
            import pyttsx3
            
            self.pyttsx3_engine = pyttsx3.init("sapi5")
            
            # Tentar usar voz portuguesa (Maria)
            voices = self.pyttsx3_engine.getProperty("voices")
            for v in voices:
                if "Maria" in v.name or "Portuguese" in v.name:
                    self.pyttsx3_engine.setProperty("voice", v.id)
                    logger.info(f"Voz selecionada: {v.name}")
                    break
            
            # Configurações padrão
            self.pyttsx3_engine.setProperty("rate", 170)
            self.pyttsx3_engine.setProperty("volume", 1.0)
            
            self.current_engine = "pyttsx3"
            logger.info("✅ pyttsx3 inicializado como fallback")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar pyttsx3: {e}")
            return False
    
    def speak(self, text: str, speed: float = 1.0, blocking: bool = True) -> bool:
        """
        Fala o texto fornecido.
        
        Args:
            text: Texto a ser falado
            speed: Velocidade (1.0 = normal, <1 = mais rápido, >1 = mais devagar)
            blocking: Se True, aguarda conclusão. Se False, fala em background.
            
        Returns:
            bool: True se sucesso
        """
        if not text or not text.strip():
            return False
        
        # Tentar Piper primeiro
        if self.piper_voice:
            try:
                return self._speak_piper(text, speed, blocking)
            except Exception as e:
                logger.error(f"Piper falhou: {e}")
                logger.info("Usando fallback pyttsx3...")
        
        # Fallback para pyttsx3
        if self.pyttsx3_engine:
            try:
                return self._speak_pyttsx3(text, speed, blocking)
            except Exception as e:
                logger.error(f"pyttsx3 falhou: {e}")
                return False
        
        logger.error("Nenhum engine TTS disponível")
        return False
    
    def _speak_piper(self, text: str, speed: float, blocking: bool) -> bool:
        """Fala usando Piper TTS."""
        import io
        import wave
        import tempfile
        
        # Sintetizar
        audio_chunks = list(self.piper_voice.synthesize(text))
        
        if not audio_chunks:
            return False
        
        # Criar WAV em memória
        audio_buffer = io.BytesIO()
        first_chunk = audio_chunks[0]
        
        with wave.open(audio_buffer, 'wb') as wav_file:
            wav_file.setnchannels(first_chunk.sample_channels)
            wav_file.setsampwidth(first_chunk.sample_width)
            
            # Ajustar sample rate baseado na velocidade
            sample_rate = int(first_chunk.sample_rate / speed)
            wav_file.setframerate(sample_rate)
            
            for chunk in audio_chunks:
                wav_file.writeframes(chunk.audio_int16_bytes)
        
        # Salvar em arquivo temporário
        audio_buffer.seek(0)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_buffer.read())
            temp_audio_file = temp_file.name
        
        # Reproduzir
        return self._play_audio(temp_audio_file, blocking)
    
    def _speak_pyttsx3(self, text: str, speed: float, blocking: bool) -> bool:
        """Fala usando pyttsx3."""
        # Ajustar velocidade
        rate = int(170 / speed)
        self.pyttsx3_engine.setProperty("rate", rate)
        
        self.pyttsx3_engine.say(text)
        
        if blocking:
            self.pyttsx3_engine.runAndWait()
        
        return True
    
    def _play_audio(self, audio_file: str, blocking: bool) -> bool:
        """Reproduz arquivo de áudio."""
        try:
            # Tentar pygame primeiro
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                
                if blocking:
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                
                return True
            except ImportError:
                pass
            
            # Fallback winsound (Windows)
            import winsound
            if blocking:
                winsound.PlaySound(audio_file, winsound.SND_FILENAME)
            else:
                winsound.PlaySound(audio_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao reproduzir áudio: {e}")
            return False
    
    def stop(self):
        """Para a fala atual."""
        try:
            if self.pyttsx3_engine:
                self.pyttsx3_engine.stop()
            
            # Parar pygame se estiver tocando
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
        except:
            pass
    
    def get_info(self) -> dict:
        """Retorna informações sobre o engine atual."""
        return {
            "engine": self.current_engine,
            "piper_available": self.piper_voice is not None,
            "pyttsx3_available": self.pyttsx3_engine is not None,
        }


# Uso e teste
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🎤 Testando AstraTTS\n")
    
    # Criar TTS
    tts = AstraTTS()
    
    # Mostrar info
    info = tts.get_info()
    print(f"Engine ativo: {info['engine']}")
    print(f"Piper disponível: {info['piper_available']}")
    print(f"pyttsx3 disponível: {info['pyttsx3_available']}\n")
    
    # Testar velocidades
    print("🗣️ Testando velocidade normal...")
    tts.speak("Olá! Eu sou a Astra, e posso falar em diferentes velocidades.", speed=1.0)
    
    print("🗣️ Testando velocidade rápida...")
    tts.speak("Agora estou a falar mais rápido.", speed=0.8)
    
    print("🗣️ Testando velocidade devagar...")
    tts.speak("E agora mais devagar.", speed=1.2)
    
    print("\n✅ Teste concluído!")

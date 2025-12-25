#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Sistema de Detecção de Hotword (Wake Word)
Sistema para detectar palavras de ativação como "Astra", "ASTRA", etc.

Funcionalidades:
- Detecção contínua de wake words
- Múltiplas palavras de ativação configuráveis
- Sistema de fallback se bibliotecas especializadas não estiverem disponíveis
- Integração com sistema de microfone existente
"""

import logging
import os
import threading
import time
import re
from typing import List, Callable, Optional
from enum import Enum

# Configurar logger
logger = logging.getLogger(__name__)

class HotwordEngine(Enum):
    """Engines disponíveis para detecção de hotword."""
    PORCUPINE = "porcupine"
    VOSK = "vosk" 
    SIMPLE_STT = "simple_stt"  # Fallback usando SpeechRecognition

class HotwordStatus(Enum):
    """Estados do detector de hotword."""
    IDLE = "idle"
    LISTENING = "listening"
    DETECTED = "detected"
    ERROR = "error"

class HotwordDetector:
    """
    Sistema de detecção de wake words para ASTRA.
    Suporta múltiplos engines e palavras de ativação.
    """
    
    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Inicializa o detector de hotword.
        
        Args:
            status_callback: Função para receber atualizações de status
        """
        self.status_callback = status_callback
        self.status = HotwordStatus.IDLE
        self.current_engine = None
        
        # Palavras de ativação padrão
        self.wake_words = [
            "Astra", "ASTRA", "assistente", "hey ASTRA", "ola ASTRA",
            "ei ASTRA", "ASTRA ajuda", "ASTRA preciso"
        ]
        
        # Configurações
        self.sensitivity = 0.7  # Sensibilidade de detecção (0.0 - 1.0)
        self.is_listening = False
        self.detection_callback = None
        
        # Threads de controle
        self.listen_thread = None
        self._shutdown = False
        
        # Inicializar engine
        self.initialize_engine()
    
    def set_status(self, message: str, status: HotwordStatus = None):
        """Atualiza status do detector."""
        if status:
            self.status = status
            
        if self.status_callback:
            self.status_callback(f"[HOTWORD-{self.status.value.upper()}] {message}")
            
        logger.info(f"Hotword Detector: {message}")
    
    def initialize_engine(self) -> bool:
        """Inicializa o engine de detecção mais apropriado."""
        self.set_status("🔄 Inicializando detector de hotword...", HotwordStatus.IDLE)
        
        # Tentar Porcupine primeiro (mais preciso)
        if self._init_porcupine():
            self.current_engine = HotwordEngine.PORCUPINE
            self.set_status("✅ Porcupine hotword detector carregado", HotwordStatus.IDLE)
            return True
        
        # Tentar Vosk como segunda opção
        if self._init_vosk():
            self.current_engine = HotwordEngine.VOSK
            self.set_status("✅ Vosk hotword detector carregado", HotwordStatus.IDLE)
            return True
        
        # Fallback para sistema simples
        if self._init_simple_stt():
            self.current_engine = HotwordEngine.SIMPLE_STT
            self.set_status("✅ Simple STT hotword detector carregado", HotwordStatus.IDLE)
            return True
        
        self.set_status("❌ Nenhum engine de hotword disponível", HotwordStatus.ERROR)
        return False
    
    def _init_porcupine(self) -> bool:
        """Tenta inicializar Porcupine."""
        try:
            import pvporcupine
            
            # Verificar palavras-chave disponíveis no Porcupine
            available_keywords = list(pvporcupine.KEYWORDS.keys()) if hasattr(pvporcupine, 'KEYWORDS') else []
            
            if not available_keywords:
                logger.info("Nenhuma palavra-chave Porcupine disponível")
                return False
            
            # Selecionar palavras-chave disponíveis
            selected_keywords = []
            for keyword in ['computer', 'ASTRAa', 'Astra']:
                if keyword in available_keywords:
                    selected_keywords.append(keyword)
            
            if not selected_keywords:
                # Usar primeira palavra disponível como fallback
                selected_keywords = [available_keywords[0]]
            
            # Criar instância do Porcupine (versão gratuita)
            self.porcupine = pvporcupine.create(
                keywords=selected_keywords,
                sensitivities=[self.sensitivity] * len(selected_keywords)
            )
            
            self.porcupine_keywords = selected_keywords
            
            logger.info(f"Porcupine inicializado com {len(self.porcupine_keywords)} palavras-chave")
            return True
            
        except ImportError:
            logger.info("Porcupine não instalado. Use: pip install pvporcupine")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar Porcupine: {e}")
            return False
    
    def _init_vosk(self) -> bool:
        """Tenta inicializar Vosk."""
        try:
            import vosk
            import json
            
            # Verificar se há modelo Vosk disponível
            model_path = "models/vosk-model-small-pt-0.3"
            if not os.path.exists(model_path):
                logger.info("Modelo Vosk não encontrado. Download necessário.")
                return False
            
            self.vosk_model = vosk.Model(model_path)
            self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
            
            logger.info("Vosk inicializado com sucesso")
            return True
            
        except ImportError:
            logger.info("Vosk não instalado. Use: pip install vosk")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar Vosk: {e}")
            return False
    
    def _init_simple_stt(self) -> bool:
        """Inicializa sistema simples usando SpeechRecognition."""
        try:
            import speech_recognition as sr
            
            self.recognizer = sr.Recognizer()
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 300
            self.recognizer.pause_threshold = 0.5
            
            logger.info("Simple STT hotword detector inicializado")
            return True
            
        except ImportError:
            logger.error("SpeechRecognition não instalado")
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar Simple STT: {e}")
            return False
    
    def add_wake_word(self, word: str):
        """Adiciona uma nova palavra de ativação."""
        if word.lower() not in [w.lower() for w in self.wake_words]:
            self.wake_words.append(word.lower())
            logger.info(f"Wake word adicionada: {word}")
    
    def remove_wake_word(self, word: str):
        """Remove uma palavra de ativação."""
        self.wake_words = [w for w in self.wake_words if w.lower() != word.lower()]
        logger.info(f"Wake word removida: {word}")
    
    def set_detection_callback(self, callback: Callable[[str], None]):
        """Define callback para quando hotword for detectado."""
        self.detection_callback = callback
    
    def start_listening(self) -> bool:
        """Inicia escuta contínua por hotwords."""
        if self.is_listening:
            return True
        
        if not self.current_engine:
            self.set_status("❌ Nenhum engine disponível", HotwordStatus.ERROR)
            return False
        
        self.is_listening = True
        self._shutdown = False
        
        # Iniciar thread de escuta
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        
        self.set_status("🎙️ Escutando por wake words...", HotwordStatus.LISTENING)
        return True
    
    def stop_listening(self):
        """Para a escuta contínua."""
        self.is_listening = False
        self._shutdown = True
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        
        self.set_status("🛑 Escuta de hotword parada", HotwordStatus.IDLE)
    
    def _listen_loop(self):
        """Loop principal de escuta."""
        if self.current_engine == HotwordEngine.PORCUPINE:
            self._listen_with_porcupine()
        elif self.current_engine == HotwordEngine.VOSK:
            self._listen_with_vosk()
        elif self.current_engine == HotwordEngine.SIMPLE_STT:
            self._listen_with_simple_stt()
    
    def _listen_with_porcupine(self):
        """Escuta usando Porcupine."""
        try:
            import pyaudio
            
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.porcupine.sample_rate,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            
            while self.is_listening and not self._shutdown:
                pcm = stream.read(self.porcupine.frame_length)
                pcm = [int(x) for x in pcm]
                
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    detected_word = ["computer", "ASTRAa"][keyword_index]
                    self._on_hotword_detected(detected_word)
                    time.sleep(1)  # Pausa após detecção
            
            stream.close()
            audio.terminate()
            
        except Exception as e:
            logger.error(f"Erro na escuta Porcupine: {e}")
            self.set_status(f"❌ Erro Porcupine: {e}", HotwordStatus.ERROR)
    
    def _listen_with_vosk(self):
        """Escuta usando Vosk."""
        try:
            import pyaudio
            import json
            
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000
            )
            
            while self.is_listening and not self._shutdown:
                data = stream.read(4000, exception_on_overflow=False)
                if self.vosk_rec.AcceptWaveform(data):
                    result = json.loads(self.vosk_rec.Result())
                    text = result.get('text', '').lower()
                    
                    # Verificar se alguma wake word foi detectada
                    for wake_word in self.wake_words:
                        if wake_word in text:
                            self._on_hotword_detected(wake_word)
                            time.sleep(1)
                            break
            
            stream.close()
            audio.terminate()
            
        except Exception as e:
            logger.error(f"Erro na escuta Vosk: {e}")
            self.set_status(f"❌ Erro Vosk: {e}", HotwordStatus.ERROR)
    
    def _listen_with_simple_stt(self):
        """Escuta usando SpeechRecognition (fallback)."""
        try:
            import speech_recognition as sr
            
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_listening and not self._shutdown:
                try:
                    with sr.Microphone() as source:
                        # Escuta com timeout baixo para responsividade
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        
                    # Reconhecer com Google (offline seria melhor, mas requer setup)
                    text = self.recognizer.recognize_google(audio, language="pt-PT").lower()
                    
                    # Verificar wake words
                    for wake_word in self.wake_words:
                        if wake_word in text:
                            self._on_hotword_detected(wake_word)
                            time.sleep(1)
                            break
                            
                except sr.WaitTimeoutError:
                    continue  # Timeout normal, continuar escutando
                except sr.UnknownValueError:
                    continue  # Não entendeu, continuar
                except Exception as e:
                    logger.error(f"Erro na escuta Simple STT: {e}")
                    time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Erro na configuração Simple STT: {e}")
            self.set_status(f"❌ Erro Simple STT: {e}", HotwordStatus.ERROR)
    
    def _on_hotword_detected(self, detected_word: str):
        """Callback interno quando hotword é detectado."""
        self.set_status(f"✅ Wake word detectado: {detected_word}", HotwordStatus.DETECTED)
        
        if self.detection_callback:
            try:
                self.detection_callback(detected_word)
            except Exception as e:
                logger.error(f"Erro no callback de detecção: {e}")
        
        # Voltar ao estado de escuta
        self.set_status("🎙️ Voltando à escuta...", HotwordStatus.LISTENING)
    
    def get_status_info(self) -> dict:
        """Retorna informações de status do detector."""
        return {
            'status': self.status.value,
            'engine': self.current_engine.value if self.current_engine else None,
            'is_listening': self.is_listening,
            'wake_words': self.wake_words,
            'sensitivity': self.sensitivity
        }
    
    def shutdown(self):
        """Desliga o detector e limpa recursos."""
        self.stop_listening()
        
        # Limpar recursos específicos do engine
        if self.current_engine == HotwordEngine.PORCUPINE:
            try:
                if hasattr(self, 'porcupine'):
                    self.porcupine.delete()
            except:
                pass
        
        self.set_status("🛑 Detector de hotword desligado", HotwordStatus.IDLE)


# Função utilitária para criar detector com configuração padrão
def create_hotword_detector(status_callback: Optional[Callable[[str], None]] = None) -> HotwordDetector:
    """
    Cria um detector de hotword com configuração padrão.
    
    Args:
        status_callback: Função para receber updates de status
        
    Returns:
        HotwordDetector: Instância configurada do detector
    """
    detector = HotwordDetector(status_callback)
    
    # Adicionar wake words específicas do ASTRA
    wake_words_ASTRA = [
        "Astra", "ASTRA", "hey ASTRA", "ola ASTRA", "ei ASTRA",
        "ASTRA ajuda", "ASTRA preciso", "assistente"
    ]
    
    for word in wake_words_ASTRA:
        detector.add_wake_word(word)
    
    return detector


if __name__ == "__main__":
    # Teste do sistema
    def on_status(message):
        print(f"Status: {message}")
    
    def on_detection(word):
        print(f"🎯 WAKE WORD DETECTADO: {word}")
    
    detector = create_hotword_detector(on_status)
    detector.set_detection_callback(on_detection)
    
    print("Iniciando teste de detecção de hotword...")
    print("Diga 'Astra', 'ASTRA' ou outra wake word.")
    print("Pressione Ctrl+C para sair.")
    
    detector.start_listening()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando detector...")
        detector.shutdown()


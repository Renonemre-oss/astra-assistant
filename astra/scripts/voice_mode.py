#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Modo Astra (Voice-Only)
Executa o assistente em modo somente voz, sem interface gráfica.
Sistema fica sempre escutando por "Astra" automaticamente.

Uso:
    python Astra_voice_mode.py

Comandos especiais:
    - "Astra, sair" ou "Astra, desligar" -> Encerra o programa
    - "Astra, ajuda" -> Mostra comandos disponíveis
"""

import sys
import time
import signal
import logging
import threading
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports do projeto
from ..config import CONFIG
from utils.utils import perguntar_ollama
from audio.audio_manager import AudioManager

# Sistema de personalidade
try:
    from modules.personality_engine import PersonalityEngine
    PERSONALITY_AVAILABLE = True
except ImportError:
    print("⚠️ Sistema de personalidade não disponível")
    PERSONALITY_AVAILABLE = False

# Sistema de memória
try:
    from modules.memory_system import MemorySystem
    MEMORY_AVAILABLE = True
except ImportError:
    print("⚠️ Sistema de memória não disponível")
    MEMORY_AVAILABLE = False

# Sistema de hotword
try:
    from voice.hotword_detector import create_hotword_detector
    HOTWORD_AVAILABLE = True
except ImportError:
    print("❌ Sistema de hotword não disponível!")
    print("Execute: python scripts/setup_voice_system.py auto")
    HOTWORD_AVAILABLE = False

# STT
try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    print("❌ SpeechRecognition não disponível!")
    print("Execute: pip install speechrecognition")
    STT_AVAILABLE = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/Astra_voice.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AstraVoiceMode:
    """
    Modo de voz do ASTRA - funciona apenas com comandos de voz.
    """
    
    def __init__(self):
        """Inicializa o modo de voz."""
        self.running = False
        self.hotword_detector = None
        self.audio_manager = None
        self.recognizer = None
        self.personality_engine = None
        self.memory_system = None
        
        # Controle de shutdown
        self.shutdown_requested = False
        
        # Histórico simples
        self.conversation_history = []
        
        print("🤖 ASTRA - Modo Astra (Somente Voz)")
        print("=" * 40)
    
    def initialize_systems(self):
        """Inicializa todos os sistemas necessários."""
        print("🔄 Inicializando sistemas...")
        
        # 1. Sistema de áudio (TTS)
        try:
            self.audio_manager = AudioManager()
            self.audio_manager.load_tts_model()
            print("✅ Sistema TTS inicializado")
        except Exception as e:
            print(f"❌ Erro no TTS: {e}")
            return False
        
        # 2. Sistema STT
        if STT_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 300
                self.recognizer.pause_threshold = 0.5
                print("✅ Sistema STT inicializado")
            except Exception as e:
                print(f"❌ Erro no STT: {e}")
                return False
        else:
            return False
        
        # 3. Sistema de hotword
        if HOTWORD_AVAILABLE:
            try:
                self.hotword_detector = create_hotword_detector(self.on_status_update)
                self.hotword_detector.set_detection_callback(self.on_wake_word_detected)
                print("✅ Sistema Astra inicializado")
            except Exception as e:
                print(f"❌ Erro no Hotword: {e}")
                return False
        else:
            return False
        
        # 4. Sistema de personalidade
        if PERSONALITY_AVAILABLE:
            try:
                self.personality_engine = PersonalityEngine()
                print("✅ Sistema de Personalidade inicializado")
            except Exception as e:
                print(f"⚠️ Personalidade não disponível: {e}")
        
        # 5. Sistema de memória
        if MEMORY_AVAILABLE:
            try:
                self.memory_system = MemorySystem()
                print("✅ Sistema de Memória inicializado")
            except Exception as e:
                print(f"⚠️ Memória não disponível: {e}")
        
        return True
    
    def on_status_update(self, message):
        """Callback para atualizações de status."""
        logger.info(f"Status: {message}")
    
    def on_wake_word_detected(self, wake_word):
        """Callback quando Astra é detectado."""
        print(f"\n🎯 '{wake_word.upper()}' DETECTADO!")
        self.speak(f"Sim, estou escutando.")
        
        # Escutar comando
        command = self.listen_for_command()
        if command:
            print(f"💬 Comando: {command}")
            self.process_command(command)
        else:
            print("❌ Nenhum comando detectado")
            self.speak("Não consegui ouvir seu comando. Tente novamente.")
    
    def listen_for_command(self, timeout=10):
        """Escuta comando após wake word."""
        if not self.recognizer:
            return None
        
        try:
            print("🎙️ Escutando comando...")
            
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
            
            # Reconhecer
            command = self.recognizer.recognize_google(audio, language="pt-PT")
            return command.strip()
            
        except sr.WaitTimeoutError:
            print("⏰ Timeout - nenhum comando")
            return None
        except sr.UnknownValueError:
            print("❓ Não entendi o comando")
            return None
        except Exception as e:
            print(f"❌ Erro ao escutar: {e}")
            return None
    
    def process_command(self, command):
        """Processa comando de voz."""
        command_lower = command.lower().strip()
        
        # Comandos de controle
        if any(word in command_lower for word in ["sair", "desligar", "tchau", "até logo"]):
            self.speak("Ok, até logo!")
            self.shutdown_requested = True
            return
        
        if "ajuda" in command_lower:
            help_text = """
            Comandos disponíveis:
            - Pergunte qualquer coisa que eu respondo
            - Diga 'que horas são' para saber a hora
            - Diga 'sair' ou 'desligar' para encerrar
            - Diga 'ajuda' para ver esta mensagem
            """
            self.speak(help_text)
            print("💡 Ajuda exibida")
            return
        
        # Comandos de hora/data
        if any(word in command_lower for word in ["horas", "hora", "data", "dia"]):
            from datetime import datetime
            now = datetime.now()
            
            if any(word in command_lower for word in ["horas", "hora"]):
                response = f"Agora são {now.strftime('%H:%M')}"
            else:
                days = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']
                months = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                         'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
                day_name = days[now.weekday()]
                month_name = months[now.month - 1]
                response = f"Hoje é {day_name}, {now.day} de {month_name} de {now.year}"
            
            self.speak(response)
            print(f"🕐 Resposta: {response}")
            return
        
        # Comando geral - usar Ollama
        try:
            print("🤔 Processando com Ollama...")
            self.speak("Deixe-me pensar...")
            
            # Criar contexto da conversa
            history_text = "\n".join([
                f"{item['role']}: {item['content']}" 
                for item in self.conversation_history[-5:]  # Últimas 5 mensagens
            ])
            
            # Obter contexto de memória se disponível
            memory_context = ""
            if self.memory_system:
                try:
                    memory_context = self.memory_system.get_relevant_context(command, max_memories=3)
                    if memory_context:
                        print(f"🧠 Usando memórias relevantes")
                except Exception as e:
                    logger.error(f"Erro ao obter contexto de memória: {e}")
            
            # Criar prompt com contexto
            context_parts = []
            if history_text:
                context_parts.append(f"Histórico: {history_text}")
            if memory_context:
                context_parts.append(memory_context)
            
            context_str = "\n\n".join(context_parts) if context_parts else ""
            
            prompt = f"""Tu és o ASTRA, um assistente virtual casual e amigável. 
            Responde de forma natural e direta.

{context_str}

Utilizador: {command}"""
            
            response = perguntar_ollama(prompt)
            
            if response and response.strip():
                # Aplicar personalidade se disponível
                user_emotions = []
                personality_used = None
                if self.personality_engine:
                    try:
                        response, personality_used = self.personality_engine.process_user_interaction(command, response)
                        print(f"🎭 Personalidade: {personality_used.value}")
                        user_emotions = [self.personality_engine.current_mood.value] if self.personality_engine.current_mood else []
                    except Exception as e:
                        logger.error(f"Erro ao aplicar personalidade: {e}")
                
                # Armazenar na memória se disponível
                if self.memory_system:
                    try:
                        context_info = {
                            'mode': 'voice',
                            'personality_mode': personality_used.value if personality_used else 'unknown'
                        }
                        
                        self.memory_system.store_conversation_turn(
                            user_input=command,
                            assistant_response=response,
                            user_emotions=user_emotions,
                            context=context_info
                        )
                        print(f"🧠 Armazenado na memória")
                    except Exception as e:
                        logger.error(f"Erro ao armazenar na memória: {e}")
                
                self.speak(response)
                print(f"🤖 Resposta: {response[:100]}...")
                
                # Salvar no histórico
                self.conversation_history.extend([
                    {"role": "user", "content": command},
                    {"role": "assistant", "content": response}
                ])
                
                # Manter apenas últimas 10 interações
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
            else:
                self.speak("Desculpe, não consegui processar sua pergunta.")
                
        except Exception as e:
            logger.error(f"Erro ao processar comando: {e}")
            self.speak("Ocorreu um erro. Tente novamente.")
    
    def speak(self, text):
        """Fala um texto usando TTS."""
        if self.audio_manager:
            self.audio_manager.text_to_speech(text)
        print(f"🗣️ ASTRA: {text}")
    
    def start(self):
        """Inicia o modo de voz."""
        if not self.initialize_systems():
            print("❌ Falha na inicialização!")
            return
        
        print("\n🎯 MODO Astra ATIVO!")
        print("💡 Diga 'Astra' seguido do seu comando")
        print("💡 Exemplos:")
        print("   - Astra, que horas são?")
        print("   - Astra, como está o tempo?")
        print("   - Astra, conte-me uma piada")
        print("   - Astra, sair")
        print("\n⏳ Aguardando comando...")
        
        self.speak("Sistema Astra ativo. Como posso ajudá-lo?")
        
        # Iniciar detecção de hotword
        if self.hotword_detector.start_listening():
            self.running = True
            print("✅ Escuta ativa - sistema pronto!")
            
            try:
                # Loop principal
                while self.running and not self.shutdown_requested:
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\n🛑 Interrompido pelo usuário")
            
        else:
            print("❌ Erro ao iniciar escuta")
        
        self.shutdown()
    
    def shutdown(self):
        """Encerra o sistema."""
        print("\n🛑 Encerrando sistema...")
        self.running = False
        
        if self.hotword_detector:
            self.hotword_detector.shutdown()
        
        if self.audio_manager:
            self.audio_manager.shutdown()
        
        print("👋 Sistema encerrado!")


def signal_handler(signum, frame):
    """Handler para sinais do sistema."""
    print("\n🛑 Sinal de encerramento recebido...")
    global Astra
    if Astra:
        Astra.shutdown_requested = True


def main():
    """Função principal."""
    global Astra
    
    # Configurar handler de sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Verificar dependências
    if not HOTWORD_AVAILABLE or not STT_AVAILABLE:
        print("\n❌ Dependências não disponíveis!")
        print("Execute o setup primeiro:")
        print("  python scripts/setup_voice_system.py auto")
        return
    
    # Iniciar modo Astra
    Astra = AstraVoiceMode()
    Astra.start()


if __name__ == "__main__":
    main()


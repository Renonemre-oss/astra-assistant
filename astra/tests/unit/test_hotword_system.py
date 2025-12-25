#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Teste do Sistema de Hotword
Teste simples para verificar se o sistema de detecção de wake words está funcionando.
"""

import sys
import time
import logging
from pathlib import Path

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Testa imports necessários."""
    print("🧪 Testando imports...")
    
    try:
        from voice.hotword_detector import create_hotword_detector, HotwordDetector
        print("✅ Hotword detector importado com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar hotword detector: {e}")
        return False

def test_detector_creation():
    """Testa criação do detector."""
    print("\n🧪 Testando criação do detector...")
    
    try:
        from voice.hotword_detector import create_hotword_detector
        
        def status_callback(message):
            print(f"📢 Status: {message}")
        
        detector = create_hotword_detector(status_callback)
        print("✅ Detector criado com sucesso")
        
        # Verificar status
        status_info = detector.get_status_info()
        print(f"🔍 Engine: {status_info['engine']}")
        print(f"🔍 Status: {status_info['status']}")
        print(f"🔍 Wake words: {status_info['wake_words']}")
        
        detector.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar detector: {e}")
        return False

def test_interactive_hotword():
    """Teste interativo do hotword detector."""
    print("\n🧪 Teste interativo do hotword detector")
    print("Pressione Ctrl+C para sair\n")
    
    try:
        from voice.hotword_detector import create_hotword_detector
        
        def status_callback(message):
            print(f"📢 {message}")
        
        def detection_callback(word):
            print(f"🎯 WAKE WORD DETECTADO: '{word}'")
            print("💬 Agora você pode falar seu comando...")
        
        # Criar detector
        detector = create_hotword_detector(status_callback)
        detector.set_detection_callback(detection_callback)
        
        print("🚀 Iniciando detector...")
        print("💡 Diga uma das palavras: Astra, ASTRA, hey ASTRA, assistente")
        print("⏳ Aguardando wake word...\n")
        
        # Iniciar escuta
        if detector.start_listening():
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n🛑 Parando detector...")
        else:
            print("❌ Erro ao iniciar detector")
        
        detector.shutdown()
        
    except ImportError as e:
        print(f"❌ Sistema não disponível: {e}")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def test_system_info():
    """Mostra informações do sistema."""
    print("\n📋 Informações do Sistema")
    print("=" * 30)
    
    # PyAudio
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        device_count = audio.get_device_count()
        print(f"🎤 PyAudio: {device_count} dispositivos disponíveis")
        
        # Listar microfones
        print("🎙️ Microfones disponíveis:")
        for i in range(device_count):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  {i}: {info['name']}")
        
        audio.terminate()
    except Exception as e:
        print(f"❌ PyAudio: {e}")
    
    # SpeechRecognition
    try:
        import speech_recognition as sr
        print("✅ SpeechRecognition disponível")
    except ImportError:
        print("❌ SpeechRecognition não instalado")
    
    # Porcupine
    try:
        import pvporcupine
        print("✅ Porcupine disponível")
    except ImportError:
        print("❌ Porcupine não instalado")
    
    # Vosk
    try:
        import vosk
        print("✅ Vosk disponível")
    except ImportError:
        print("❌ Vosk não instalado")
    
    # Verificar modelos
    models_dir = project_root / "models"
    if models_dir.exists():
        models = list(models_dir.glob("vosk-model-*"))
        if models:
            print(f"📁 Modelos Vosk encontrados: {len(models)}")
            for model in models:
                print(f"  📂 {model.name}")
        else:
            print("📁 Nenhum modelo Vosk encontrado")
    else:
        print("📁 Diretório de modelos não existe")

def main():
    """Função principal do teste."""
    print("🤖 ASTRA - Teste do Sistema de Hotword")
    print("=" * 40)
    
    # Teste de sistema
    test_system_info()
    
    # Testes básicos
    if not test_imports():
        print("\n❌ Falha nos imports - verifique instalação")
        return
    
    if not test_detector_creation():
        print("\n❌ Falha na criação do detector")
        return
    
    # Menu interativo
    while True:
        print("\n🔧 Opções de Teste:")
        print("1. 🎙️ Teste interativo de hotword")
        print("2. 📋 Informações do sistema") 
        print("3. 🚪 Sair")
        
        choice = input("\nEscolha (1-3): ").strip()
        
        if choice == "1":
            test_interactive_hotword()
        elif choice == "2":
            test_system_info()
        elif choice == "3":
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()


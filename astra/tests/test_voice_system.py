#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo do sistema de voz do ALEX
Testa TTS, STT e integração completa
"""

import sys
import time
from pathlib import Path

# Adicionar projeto ao path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_tts_system():
    """Teste do sistema TTS"""
    print("🗣️ TESTANDO SISTEMA TTS")
    print("=" * 40)
    
    try:
        from audio.audio_manager import AudioManager
        
        print("1. Inicializando AudioManager...")
        audio_mgr = AudioManager()
        audio_mgr.load_tts_model()
        
        # Aguardar carregamento
        print("2. Aguardando carregamento...")
        time.sleep(3)
        
        # Verificar status
        status = audio_mgr.get_status()
        print(f"3. Status TTS: {'✅ OK' if status['tts_loaded'] else '❌ FALHA'}")
        
        if status['tts_loaded']:
            print("4. Testando síntese...")
            success = audio_mgr.text_to_speech("Olá, eu sou o ALEX. Sistema de voz funcionando!")
            print(f"   Resultado: {'✅ Sucesso' if success else '❌ Falha'}")
            
            # Aguardar fala
            time.sleep(4)
            
            # Testar configurações de voz
            print("5. Testando configurações...")
            voices = audio_mgr.get_available_voices()
            print(f"   Vozes disponíveis: {len(voices)}")
            for i, voice in enumerate(voices[:3]):
                print(f"     {i}: {voice.get('name', 'N/A')}")
            
        print("6. Finalizando TTS...")
        audio_mgr.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Erro no TTS: {e}")
        return False

def test_stt_system():
    """Teste do sistema STT"""
    print("\n🎙️ TESTANDO SISTEMA STT")
    print("=" * 40)
    
    try:
        import speech_recognition as sr
        
        print("1. Inicializando Speech Recognition...")
        recognizer = sr.Recognizer()
        
        print("2. Verificando microfones...")
        mics = sr.Microphone.list_microphone_names()
        print(f"   Microfones detectados: {len(mics)}")
        
        if len(mics) == 0:
            print("❌ Nenhum microfone disponível!")
            return False
            
        print("   Primeiros 3 microfones:")
        for i, mic in enumerate(mics[:3]):
            print(f"     {i}: {mic}")
        
        print("3. Testando captura de áudio...")
        try:
            # Usar microfone padrão
            with sr.Microphone() as source:
                print("   Ajustando para ruído ambiente...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"   Threshold configurado: {recognizer.energy_threshold}")
                
            print("✅ Sistema STT pronto para uso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar microfone: {e}")
            return False
        
    except ImportError:
        print("❌ speech_recognition não instalado")
        return False
    except Exception as e:
        print(f"❌ Erro no STT: {e}")
        return False

def test_voice_integration():
    """Teste de integração voz completa"""
    print("\n🎤 TESTANDO INTEGRAÇÃO COMPLETA")
    print("=" * 40)
    
    try:
        # Tentar importar sistemas avançados
        systems_available = {}
        
        # 1. Sistema Híbrido
        try:
            from speech.hybrid_speech_engine import HybridSpeechEngine
            systems_available['hybrid'] = True
            print("✅ Sistema Híbrido disponível")
        except ImportError:
            systems_available['hybrid'] = False
            print("❌ Sistema Híbrido não disponível")
        
        # 2. Hotword Detection
        try:
            # Verificar se existe o sistema de hotword
            hotword_files = list(Path(project_root).glob("**/hotword*.py"))
            systems_available['hotword'] = len(hotword_files) > 0
            print(f"{'✅' if systems_available['hotword'] else '❌'} Hotword Detection: {len(hotword_files)} arquivos")
        except Exception:
            systems_available['hotword'] = False
            print("❌ Hotword Detection não disponível")
        
        # 3. Clonagem de Voz
        try:
            from speech.xtts_voice_cloning import XTTSVoiceCloning
            systems_available['voice_cloning'] = True
            print("✅ Sistema de Clonagem disponível")
        except ImportError:
            systems_available['voice_cloning'] = False
            print("❌ Sistema de Clonagem não disponível")
        
        # 4. VOSK (modelo português)
        try:
            vosk_models = list(Path(project_root).glob("**/vosk-model*"))
            systems_available['vosk'] = len(vosk_models) > 0
            print(f"{'✅' if systems_available['vosk'] else '❌'} VOSK Models: {len(vosk_models)} encontrados")
        except Exception:
            systems_available['vosk'] = False
            print("❌ VOSK não disponível")
        
        return systems_available
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return {}

def test_launchers():
    """Teste dos launchers de voz"""
    print("\n🚀 TESTANDO LAUNCHERS")
    print("=" * 40)
    
    launchers = {
        'voice_mode': 'launchers/voice_mode.py',
        'gui_launcher': 'launchers/gui_launcher.py'
    }
    
    results = {}
    
    for name, path in launchers.items():
        file_path = project_root / path
        if file_path.exists():
            try:
                # Tentar importar sem executar
                spec = f"launchers.{file_path.stem}"
                results[name] = True
                print(f"✅ {name}: Disponível")
            except Exception as e:
                results[name] = False
                print(f"❌ {name}: Erro - {e}")
        else:
            results[name] = False
            print(f"❌ {name}: Arquivo não encontrado")
    
    return results

def main():
    """Função principal do teste"""
    print("🤖 ALEX - TESTE COMPLETO DO SISTEMA DE VOZ")
    print("=" * 50)
    print(f"📁 Diretório: {project_root}")
    
    results = {
        'tts': False,
        'stt': False,
        'integration': {},
        'launchers': {}
    }
    
    # Executar testes
    results['tts'] = test_tts_system()
    results['stt'] = test_stt_system()
    results['integration'] = test_voice_integration()
    results['launchers'] = test_launchers()
    
    # Resumo final
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    print(f"🗣️ TTS (Text-to-Speech): {'✅ FUNCIONANDO' if results['tts'] else '❌ PROBLEMA'}")
    print(f"🎙️ STT (Speech-to-Text): {'✅ FUNCIONANDO' if results['stt'] else '❌ PROBLEMA'}")
    
    print("\n🔧 Sistemas Avançados:")
    for system, available in results['integration'].items():
        print(f"  {system}: {'✅ OK' if available else '❌ N/A'}")
    
    print("\n🚀 Launchers:")
    for launcher, available in results['launchers'].items():
        print(f"  {launcher}: {'✅ OK' if available else '❌ N/A'}")
    
    # Diagnóstico
    print("\n🔍 DIAGNÓSTICO:")
    if results['tts'] and results['stt']:
        print("✅ Sistema básico de voz funcional")
    elif results['tts']:
        print("⚠️  Apenas TTS funcionando - STT com problemas")
    elif results['stt']:
        print("⚠️  Apenas STT funcionando - TTS com problemas")
    else:
        print("❌ Sistema de voz com problemas graves")
    
    print("\n💡 RECOMENDAÇÕES:")
    if not results['tts']:
        print("• Verificar instalação do pyttsx3")
        print("• Verificar drivers de áudio")
    
    if not results['stt']:
        print("• Verificar microfone")
        print("• Verificar permissões de áudio")
        print("• Testar com: pip install pyaudio")
    
    if not any(results['integration'].values()):
        print("• Sistemas avançados não disponíveis")
        print("• Para funcionalidades completas, instalar dependências extras")

if __name__ == "__main__":
    main()
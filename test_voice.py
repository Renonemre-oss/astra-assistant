#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico de Voz do ASTRA
Testa todos os componentes do sistema de áudio
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("🔍 DIAGNÓSTICO DO SISTEMA DE VOZ DO ASTRA")
print("=" * 60)

# Teste 1: Pygame
print("\n1️⃣ Testando Pygame...")
try:
    import pygame
    pygame.mixer.init()
    print("   ✅ Pygame: OK")
    print(f"   📊 Versão: {pygame.version.ver}")
except Exception as e:
    print(f"   ❌ Pygame: ERRO - {e}")

# Teste 2: Piper TTS
print("\n2️⃣ Testando Piper TTS...")
try:
    from piper import PiperVoice
    print("   ✅ Piper instalado: OK")
    
    # Verificar se existe modelo
    model_path = project_root / "astra" / "modules" / "speech" / "piper_models" / "pt_PT-tugao-medium.onnx"
    if model_path.exists():
        print(f"   ✅ Modelo encontrado: {model_path.name}")
    else:
        print(f"   ⚠️ Modelo não encontrado em: {model_path}")
        print(f"   📁 Verificando outros modelos...")
        models_dir = model_path.parent
        if models_dir.exists():
            models = list(models_dir.glob("*.onnx"))
            if models:
                print(f"   📂 Modelos disponíveis:")
                for m in models:
                    print(f"      - {m.name}")
            else:
                print("   ⚠️ Nenhum modelo .onnx encontrado")
        
except ImportError:
    print("   ❌ Piper não instalado")
    print("   💡 Instale com: pip install piper-tts")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Teste 3: Síntese de áudio
print("\n3️⃣ Testando Síntese de Áudio...")
try:
    from astra.modules.speech.piper_engine import PiperTTSEngine
    
    engine = PiperTTSEngine()
    print("   ✅ Engine criado")
    
    if engine.initialize():
        print("   ✅ Engine inicializado")
        
        print("   🔊 Testando síntese...")
        audio_data = engine.synthesize("Olá, este é um teste de voz do ASTRA")
        
        if audio_data:
            print(f"   ✅ Áudio sintetizado: {len(audio_data)} bytes")
            
            # Salvar para teste
            test_file = project_root / "test_audio.wav"
            with open(test_file, 'wb') as f:
                f.write(audio_data)
            print(f"   💾 Áudio salvo em: {test_file}")
            
            # Tentar reproduzir
            print("   🔊 Reproduzindo áudio...")
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(str(test_file))
                pygame.mixer.music.play()
                
                import time
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
                print("   ✅ Áudio reproduzido com sucesso!")
            except Exception as e:
                print(f"   ❌ Erro ao reproduzir: {e}")
        else:
            print("   ❌ Falha na síntese de áudio")
    else:
        print("   ❌ Falha ao inicializar engine")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    import traceback
    traceback.print_exc()

# Teste 4: Volume do sistema
print("\n4️⃣ Verificando Volume do Sistema...")
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    current_volume = volume.GetMasterVolumeLevelScalar()
    print(f"   🔊 Volume do sistema: {int(current_volume * 100)}%")
    
    if current_volume < 0.1:
        print("   ⚠️ Volume muito baixo! Considere aumentar.")
    else:
        print("   ✅ Volume adequado")
        
except ImportError:
    print("   ⚠️ pycaw não instalado (opcional)")
    print("   💡 Para verificar volume: pip install pycaw")
except Exception as e:
    print(f"   ⚠️ Não foi possível verificar volume: {e}")

# Teste 5: Dispositivos de áudio
print("\n5️⃣ Dispositivos de Áudio...")
try:
    import pygame
    pygame.mixer.init()
    
    # Informações do mixer
    freq, size, channels = pygame.mixer.get_init()
    print(f"   📊 Configuração do mixer:")
    print(f"      - Frequência: {freq} Hz")
    print(f"      - Tamanho: {size}")
    print(f"      - Canais: {channels}")
    print("   ✅ Dispositivo de áudio disponível")
    
except Exception as e:
    print(f"   ❌ Erro ao verificar dispositivos: {e}")

print("\n" + "=" * 60)
print("📋 RESUMO DO DIAGNÓSTICO")
print("=" * 60)
print("\n✅ Se todos os testes passaram, o sistema de voz está OK")
print("⚠️ Se algum teste falhou, verifique as mensagens acima")
print("\n💡 Sugestões:")
print("   - Certifique-se que o volume do sistema não está no mudo")
print("   - Verifique se os alto-falantes/fones estão conectados")
print("   - Reinicie o ASTRA após correções")
print("\n" + "=" * 60)

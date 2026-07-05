#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
sys.path.insert(0, 'C:\\Users\\antop\\Desktop\\jarvis_organized')

from astra.modules.audio.audio_manager import AudioManager

print("🧪 Testando AudioManager com Piper TTS\n")

# Criar AudioManager
am = AudioManager()

# Carregar TTS
print("Carregando TTS...")
am.load_tts_model()

# Aguardar carregamento
time.sleep(3)

# Verificar status
status = am.get_status()
print(f"\n📊 Status:")
print(f"  TTS Loaded: {status['tts_loaded']}")
print(f"  Engine Type: {status['engine_info'].get('engine_type')}")
print(f"  Engine Info: {status['engine_info']}")

# Testar fala
if status['tts_loaded']:
    print("\n🗣️ Testando síntese de voz...")
    am.text_to_speech("Olá! Eu sou o Astra usando Piper TTS neural de alta qualidade.")
    time.sleep(5)
    print("✅ Teste concluído!")
else:
    print("❌ TTS não carregado")

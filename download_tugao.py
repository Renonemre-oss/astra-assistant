#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'C:\\Users\\antop\\Desktop\\jarvis_organized')

from astra.modules.speech.piper_engine import PiperTTSEngine
import logging

logging.basicConfig(level=logging.INFO)

print("🇵🇹 Baixando modelo Português de Portugal (tugão)...\n")

# Criar engine
engine = PiperTTSEngine()

# Baixar modelo tugao
print("📥 Baixando pt_PT-tugao-medium...")
if engine.download_model("pt_PT-tugao-medium"):
    print("\n✅ Modelo baixado com sucesso!")
    
    # Testar modelo
    print("\n🧪 Testando modelo...")
    if engine.initialize("pt_PT-tugao-medium"):
        print("✅ Modelo inicializado!")
        
        # Testar síntese
        print("\n🗣️ Testando voz portuguesa...")
        engine.speak("Olá! Eu sou o Astra, a falar com sotaque português de Portugal.", blocking=True)
        
        print("\n🎉 Tudo pronto! O modelo tugão está instalado e funcionando.")
    else:
        print("❌ Erro ao inicializar modelo")
else:
    print("❌ Erro ao baixar modelo")

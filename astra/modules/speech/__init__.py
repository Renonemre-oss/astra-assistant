#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA Speech Module
Módulo de processamento de voz e áudio do ASTRA.
"""

__version__ = "1.0.0"
__author__ = "ASTRA System"

# Importações principais do módulo speech
try:
    from .speech_engine import SpeechEngine
    from .audio_recorder import AudioRecorder
    from .voice_manager import VoiceManagerGUI
    from .hybrid_speech_engine import HybridSpeechEngine
    
    __all__ = [
        'SpeechEngine',
        'AudioRecorder', 
        'VoiceManagerGUI',
        'HybridSpeechEngine'
    ]
    
except ImportError as e:
    print(f"⚠️ Aviso: Nem todos os módulos de speech estão disponíveis: {e}")
    __all__ = []

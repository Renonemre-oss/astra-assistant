#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal
Módulo de Configurações

Centraliza todas as configurações e constantes do sistema.
"""

from pathlib import Path
import logging

# Configurar logging (será configurado depois que os diretórios forem definidos)
# Por enquanto, apenas configuração básica
logger = logging.getLogger(__name__)

# ==========================
# DIRETÓRIOS E PATHS
# ==========================
# ✅ Bug #8: Usar constants.py como fonte única
try:
    from ..constants import (
        PROJECT_ROOT, ASTRA_ROOT, DATA_DIR, LOGS_DIR,
        NEURAL_DIR, CONFIG_DIR, MODELS_DIR, CACHE_DIR
    )
except ImportError:
    # Fallback se constants.py não estiver disponível
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    ASTRA_ROOT = PROJECT_ROOT
    DATA_DIR = PROJECT_ROOT / "data"
    NEURAL_DIR = PROJECT_ROOT / "neural_models"
    LOGS_DIR = PROJECT_ROOT / "logs"
    CONFIG_DIR = PROJECT_ROOT / "config"
    MODELS_DIR = DATA_DIR / "models"
    CACHE_DIR = DATA_DIR / "cache"

WORK_DIR = PROJECT_ROOT  # Manter compat. com código existente

# Criar diretórios necessários
for directory in [DATA_DIR, LOGS_DIR, MODELS_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def configure_logging():
    """Configura o sistema de logging do ASTRA."""
    # Criar o handler de arquivo com encoding UTF-8
    file_handler = logging.FileHandler(
        LOGS_DIR / 'ASTRA_assistant.log',
        encoding='utf-8'
    )
    
    # Criar o handler do console com encoding UTF-8 (se possível)
    console_handler = logging.StreamHandler()
    
    # Configurar formatação
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configurar o logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Limpar handlers existentes para evitar duplicação
    root_logger.handlers.clear()
    
    # Adicionar os handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return logging.getLogger(__name__)

# ==========================
# CONFIGURAÇÕES PRINCIPAIS
# ==========================
CONFIG = {
    # Modelo Ollama
    "ollama_model": "llama3.2",  # ✅ Corrigido: Modelo padrão mais comum
    "ollama_url": "http://localhost:11434/api/generate",
    
    # Conversação
    "conversation_history_size": 10,
    "max_retries": 3,
    "request_timeout": 120,
    
    # Arquivos de dados
    "lembretes_file": DATA_DIR / "lembretes.txt",
    "history_file": DATA_DIR / "conversation_history.json",
    "facts_file": DATA_DIR / "personal_facts.json",
    "log_file": LOGS_DIR / "ASTRA_assistant.log",
    
    # Modelo neural
    "model_file": NEURAL_DIR / "modelo.pkl",
    "intents_file": NEURAL_DIR / "dados" / "intents.json",
    
    # TTS/Audio
    "tts_model": "tts_models/pt/cv/vits",
    "temp_audio_file": PROJECT_ROOT / "audio" / "resposta_temp.wav",
}

# ==========================
# CONFIGURAÇÕES DE INTERFACE
# ==========================
UI_STYLES = {
    "main_style": """
        QWidget {
            background-color: transparent;
            color: #dddddd;
            font-family: 'Segoe UI';
        }
        QLabel#titleLabel {
            color: #FFB84D;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 15px;
            text-shadow: 0 0 15px rgba(255, 184, 77, 0.8);
        }
        QTextEdit, QLineEdit, QComboBox {
            background-color: rgba(45, 24, 16, 0.85);
            border: 1px solid rgba(220, 160, 100, 0.4);
            padding: 12px;
            border-radius: 10px;
            font-size: 15px;
            color: #f5f0e6;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: #4a4a4a;
            border-left-style: solid;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        }
        QComboBox::down-arrow {
            image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAPCAMAAAAMf+lTAAAAGFBMVEUAAAAAAAAYGBj////f398bGxsfHx8gICB0N1zYAAAAAXRSTlMAQObYZgAAACtJREFUeNpjYMACVjMzAwsDAyMEAwMLoAYIQAECIwwCAQkGEhK4DAwAAEDXAEf4oM8gAAAAAElFTkSuQmCC);
        }
        QPushButton {
            background: linear-gradient(135deg, rgba(220, 160, 100, 0.3), rgba(180, 120, 70, 0.4));
            border: 1px solid rgba(220, 160, 100, 0.6);
            padding: 10px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 16px;
            color: #f5f0e6;
        }
        QPushButton:hover { 
            background: linear-gradient(135deg, rgba(220, 160, 100, 0.4), rgba(180, 120, 70, 0.5));
            border-color: rgba(220, 160, 100, 0.8);
            box-shadow: 0 0 10px rgba(220, 160, 100, 0.3);
        }
        QPushButton:pressed { 
            background: linear-gradient(135deg, rgba(180, 120, 70, 0.5), rgba(220, 160, 100, 0.3));
        }
        #stopButton { 
            background: linear-gradient(135deg, rgba(255, 100, 100, 0.3), rgba(200, 50, 50, 0.4));
            border: 1px solid rgba(255, 100, 100, 0.5);
        }
        #stopButton:hover { 
            background: linear-gradient(135deg, rgba(255, 100, 100, 0.4), rgba(200, 50, 50, 0.5));
            border-color: rgba(255, 100, 100, 0.7);
        }
        #statusLabel {
            color: #FFB84D;
            font-size: 14px;
            qproperty-alignment: 'AlignCenter';
            text-shadow: 0 0 8px rgba(255, 184, 77, 0.6);
        }
    """
}

# ==========================
# CONFIGURAÇÕES DE PERSONALIDADES
# ==========================
PERSONALITIES = {
    "neutra": {
        "greeting": "Olá! Como posso ajudar?",
        "style": "Responde de forma equilibrada e profissional."
    },
    "amigável": {
        "greeting": "Olá! Fico feliz em falar consigo! Como está?",
        "style": "Responde de forma calorosa, amigável e entusiástica."
    },
    "formal": {
        "greeting": "Bom dia. Em que posso ser útil?",
        "style": "Responde de forma formal e concisa."
    },
    "casual": {
        "greeting": "Ei! Tudo bem? O que precisa?",
        "style": "Responde de forma descontraída e informal."
    }
}

# ==========================
# PATHS TESSERACT (OCR)
# ==========================
TESSERACT_PATHS = [
    r'C:\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
]

# ==========================
# CONFIGURAÇÕES DE BASE DE DADOS
# ==========================
DATABASE_CONFIG_FILE = WORK_DIR / "config" / "database.ini"

def check_dependencies():
    """Verifica todas as dependências do sistema e retorna status."""
    deps = {
        'PyQt6': False,
        'PyQt6_WebEngine': False,
        'TTS': False,
        'speech_recognition': False,
        'simpleaudio': False,
        'pydub': False,
        'duckduckgo_search': False,
        'requests': False,
        'sqlite3': False,
        'PIL': False,
        'pytesseract': False,
        'opencv': False,
        'nltk': False,
        'textblob': False,
        'numpy': False,
        'pandas': False,
        'scikit_learn': False,
        'joblib': False,
        'sqlalchemy': False,
        'alembic': False,
        'webrtcvad': False,
        'librosa': False,
        'soundfile': False
    }
    
    # PyQt6
    try:
        from PyQt6 import QtWidgets, QtCore, QtGui
        deps['PyQt6'] = True
    except ImportError:
        pass
        
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        deps['PyQt6_WebEngine'] = True
    except ImportError:
        pass
    
    # TTS (sem importar para evitar conflitos com matplotlib)
    try:
        # Verificar se está instalado sem importar
        import importlib.util
        spec = importlib.util.find_spec('TTS')
        deps['TTS'] = spec is not None
    except ImportError:
        deps['TTS'] = False
    
    # Speech Recognition
    try:
        import speech_recognition as sr
        deps['speech_recognition'] = True
    except ImportError:
        pass
    
    # Audio
    try:
        import simpleaudio
        deps['simpleaudio'] = True
    except ImportError:
        pass
        
    try:
        import pydub
        deps['pydub'] = True
    except ImportError:
        pass
    
    # Internet
    try:
        from duckduckgo_search import DDGS
        deps['duckduckgo_search'] = True
    except ImportError:
        pass
        
    try:
        import requests
        deps['requests'] = True
    except ImportError:
        pass
    
    # Database
    try:
        import sqlite3
        deps['sqlite3'] = True
    except ImportError:
        pass
        
    try:
        from sqlalchemy import create_engine
        deps['sqlalchemy'] = True
    except ImportError:
        pass
        
    try:
        import alembic
        deps['alembic'] = True
    except ImportError:
        pass
    
    # Image Processing
    try:
        from PIL import Image
        deps['PIL'] = True
    except ImportError:
        pass
        
    try:
        import pytesseract
        deps['pytesseract'] = True
    except ImportError:
        pass
        
    try:
        import cv2
        deps['opencv'] = True
    except ImportError:
        pass
    
    # NLP
    try:
        import nltk
        deps['nltk'] = True
    except ImportError:
        pass
        
    try:
        import textblob
        deps['textblob'] = True
    except ImportError:
        pass
    
    # ML
    try:
        import numpy
        deps['numpy'] = True
    except ImportError:
        pass

    try:
        import pandas
        deps['pandas'] = True
    except ImportError:
        pass
        
    try:
        from sklearn import __version__
        deps['scikit_learn'] = True
    except ImportError:
        pass
        
    try:
        import joblib
        deps['joblib'] = True
    except ImportError:
        pass
    
    # Voice processing
    try:
        import webrtcvad
        deps['webrtcvad'] = True
    except ImportError:
        pass
        
    try:
        import librosa
        deps['librosa'] = True
    except ImportError:
        pass
        
    try:
        import soundfile
        deps['soundfile'] = True
    except ImportError:
        pass
    
    return deps

def check_tesseract_installation():
    """Verifica se o Tesseract está instalado e configurado."""
    try:
        import pytesseract
        
        # Tentar configurar caminho do Tesseract no Windows
        for path in TESSERACT_PATHS:
            if Path(path).exists():
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract encontrado em: {path}")
                return True
        
        # Testar se funciona sem configurar caminho (Linux/Mac)
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
            
    except ImportError:
        return False

def get_database_available():
    """Verifica se o sistema de base de dados está disponível."""
    deps = check_dependencies()
    return deps.get('sqlite3', False)  # ✅ Corrigido: SQLite em vez de MySQL

def setup_tesseract():
    """Configura o Tesseract com paths automáticos e fallbacks."""
    try:
        import pytesseract
        
        for path in TESSERACT_PATHS:
            if Path(path).exists():
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract encontrado em: {path}")
                return True
        
        logger.warning("Tesseract não encontrado. OCR de imagens estará indisponível.")
        return False
    except ImportError:
        logger.warning("Pytesseract não instalado. OCR de imagens estará indisponível.")
        return False

def get_system_info():
    """Retorna informações completas do sistema e dependências."""
    deps = check_dependencies()
    tesseract_available = check_tesseract_installation()
    
    critical_missing = []
    optional_missing = []
    
    # Dependências críticas
    critical_deps = ['PyQt6', 'requests', 'numpy']
    for dep in critical_deps:
        if not deps.get(dep, False):
            critical_missing.append(dep)
    
    # Dependências opcionais mas importantes
    optional_deps = ['TTS', 'speech_recognition', 'mysql_connector', 'PIL', 'scikit_learn']
    for dep in optional_deps:
        if not deps.get(dep, False):
            optional_missing.append(dep)
    
    return {
        'dependencies': deps,
        'tesseract_available': tesseract_available,
        'database_available': get_database_available(),
        'critical_missing': critical_missing,
        'optional_missing': optional_missing,
        'total_available': sum(1 for v in deps.values() if v),
        'total_dependencies': len(deps)
    }

# ✅ Bug #15: Validar dependências críticas
def validate_critical_dependencies() -> tuple[bool, list[str]]:
    """
    Valida dependências críticas e retorna status.
    
    Returns:
        tuple: (todas_ok: bool, faltando: list[str])
    """
    system_info = get_system_info()
    critical_missing = system_info['critical_missing']
    
    if critical_missing:
        return False, critical_missing
    return True, []

def print_startup_diagnostics() -> bool:
    """
    Imprime diagnóstico de startup e retorna se deve continuar.
    
    Returns:
        bool: True se deve continuar, False se deve abortar
    """
    system_info = get_system_info()
    
    print("\n" + "="*50)
    print("🔧 ASTRA - Diagnóstico de Startup")
    print("="*50)
    
    # Dependências disponíveis
    total = system_info['total_dependencies']
    available = system_info['total_available']
    print(f"\n📊 Dependências: {available}/{total} disponíveis")
    
    # Críticas
    critical_missing = system_info['critical_missing']
    if critical_missing:
        print(f"\n❌ DEPENDÊNCIAS CRÍTICAS FALTANDO:")
        for dep in critical_missing:
            print(f"   - {dep}")
        print(f"\n⚠️  Execute: pip install {' '.join(critical_missing)}")
        print("\n❌ Não é possível iniciar sem dependências críticas.")
        print("="*50 + "\n")
        return False
    else:
        print("✅ Todas as dependências críticas disponíveis")
    
    # Opcionais
    optional_missing = system_info['optional_missing']
    if optional_missing:
        print(f"\n⚠️  Dependências opcionais faltando:")
        for dep in optional_missing:
            print(f"   - {dep}")
        print(f"\n💡 Recomendado: pip install {' '.join(optional_missing[:3])}")
    
    # Status dos sistemas
    print(f"\n💾 Database (SQLite): {'\u2705' if system_info['database_available'] else '❌'}")
    print(f"🔍 Tesseract OCR: {'\u2705' if system_info['tesseract_available'] else '❌'}")
    
    print("\n✅ Sistema pronto para iniciar!")
    print("="*50 + "\n")
    return True

# Inicializar verificação de dependências
DEPENDENCIES = check_dependencies()
TESSERACT_AVAILABLE = check_tesseract_installation()
DATABASE_AVAILABLE = get_database_available()

if __name__ == "__main__":
    print("🔧 CONFIGURAÇÕES DO ASTRA")
    print("=" * 40)
    print(f"Diretório de trabalho: {WORK_DIR}")
    print(f"Diretório de dados: {DATA_DIR}")
    print(f"Tesseract disponível: {TESSERACT_AVAILABLE}")
    print(f"Base de dados disponível: {DATABASE_AVAILABLE}")
    print("\n📦 DEPENDÊNCIAS:")
    for module, available in DEPENDENCIES.items():
        status = "✅" if available else "❌"
        print(f"{status} {module}")

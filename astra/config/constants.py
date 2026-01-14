#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASTRA - Constantes Centralizadas do Projeto
Todos os valores hardcoded devem ser definidos aqui
"""

from pathlib import Path

# ==============================================================================
# PATHS DO PROJETO
# ==============================================================================

# Diretório raiz do ASTRA
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Diretórios principais
ASTRA_ROOT = PROJECT_ROOT
DATA_DIR = ASTRA_ROOT / "data"
CONFIG_DIR = ASTRA_ROOT / "config"
LOGS_DIR = ASTRA_ROOT / "logs"
MODELS_DIR = DATA_DIR / "models"
CACHE_DIR = DATA_DIR / "cache"

# Subdiretórios de dados
MEMORY_DATA_DIR = DATA_DIR / "memory"
PERSONALITY_DATA_DIR = DATA_DIR / "personality"
CONVERSATION_DATA_DIR = DATA_DIR / "conversation"
USER_DATA_DIR = DATA_DIR / "user"
COMPANION_DATA_DIR = DATA_DIR / "companion"
VOICE_MODELS_DIR = DATA_DIR / "voice_models"

# ==============================================================================
# CONFIGURAÇÕES DE REDE
# ==============================================================================

# URLs padrão
OLLAMA_DEFAULT_URL = "http://localhost:11434"
API_SERVER_HOST = "0.0.0.0"
API_SERVER_PORT = 8000

# Timeouts (segundos)
REQUEST_TIMEOUT = 30
LLM_TIMEOUT = 60
API_TIMEOUT = 10

# ==============================================================================
# CONFIGURAÇÕES DE MEMÓRIA
# ==============================================================================

# Sistema de memória
MAX_MEMORIES = 10000
CLEANUP_THRESHOLD = 0.8  # 80% do limite
EMOTIONAL_MEMORY_DECAY_RATE = 0.15  # 15% por dia
NORMAL_MEMORY_DECAY_RATE = 0.05  # 5% por dia
EMOTIONAL_CLEANUP_DAYS = 7  # Remover memórias emocionais após 7 dias
MAX_EMOTIONAL_RATIO = 0.3  # Máximo 30% de memórias emocionais

# Tamanho da memória de trabalho
WORKING_MEMORY_SIZE = 10
CONVERSATION_HISTORY_SIZE = 50
MAX_CONTEXT_MEMORIES = 5

# ==============================================================================
# CONFIGURAÇÕES DE ÁUDIO E VOZ
# ==============================================================================

# TTS
PIPER_DEFAULT_MODEL = "pt_PT-tugao-medium"
SPEECH_RATE = 1.0
DEFAULT_LANGUAGE = "pt-PT"

# Áudio
AUDIO_SAMPLE_RATE = 22050
AUDIO_CHANNELS = 1
AUDIO_FORMAT = "wav"

# ==============================================================================
# CONFIGURAÇÕES DE PERSONALIDADE
# ==============================================================================

# Modos de personalidade disponíveis
PERSONALITY_MODES = [
    "casual", "formal", "energetic", "calm",
    "funny", "supportive", "focused", "adaptive"
]

DEFAULT_PERSONALITY = "adaptive"

# Limites de análise de humor
MOOD_CONFIDENCE_THRESHOLD = 0.6
EMOTION_INTENSITY_THRESHOLD = 0.5

# ==============================================================================
# CONFIGURAÇÕES DE IA
# ==============================================================================

# Modelos
DEFAULT_LLM_MODEL = "llama3.2"
FALLBACK_LLM_MODEL = "llama3.1"

# Cache
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hora

# Limites
MAX_TOKEN_LENGTH = 4096
MAX_RESPONSE_TIME = 30  # segundos

# ==============================================================================
# CONFIGURAÇÕES DE LOGGING
# ==============================================================================

# Níveis de log
DEFAULT_LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Arquivos de log
MAIN_LOG_FILE = "ASTRA_assistant.log"
ERROR_LOG_FILE = "errors.log"
DEBUG_LOG_FILE = "debug.log"

# Rotação de logs
MAX_LOG_SIZE_MB = 10
MAX_LOG_BACKUPS = 5

# ==============================================================================
# CONFIGURAÇÕES DE DATABASE
# ==============================================================================

# SQLite
DEFAULT_DB_PATH = "ASTRA_assistant.db"
DB_CHECK_SAME_THREAD = False
DB_TIMEOUT = 30.0
DB_FOREIGN_KEYS = True

# Limites de consultas
MAX_QUERY_RESULTS = 100
DEFAULT_PAGE_SIZE = 20

# ==============================================================================
# CONFIGURAÇÕES DE SKILLS
# ==============================================================================

# Sistema de skills
SKILLS_AUTO_LOAD = True
SKILLS_PRIORITY_ENABLED = True
MAX_SKILL_TIMEOUT = 10  # segundos

# Prioridades (valores numéricos)
SKILL_PRIORITY_CRITICAL = 100
SKILL_PRIORITY_HIGH = 75
SKILL_PRIORITY_NORMAL = 50
SKILL_PRIORITY_LOW = 25
SKILL_PRIORITY_MINIMAL = 1

# ==============================================================================
# CONFIGURAÇÕES DE UI
# ==============================================================================

# Janela principal
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
WINDOW_TITLE = "ASTRA - Assistente Pessoal"

# Cores (tema escuro)
PRIMARY_COLOR = "#007bff"
SECONDARY_COLOR = "#6c757d"
BACKGROUND_COLOR = "#2d1810"
TEXT_COLOR = "#f5f0e6"

# ==============================================================================
# CONFIGURAÇÕES DE PERFORMANCE
# ==============================================================================

# Threads
MAX_WORKER_THREADS = 4
THREAD_POOL_SIZE = 10

# Cache de performance
PERFORMANCE_CACHE_SIZE = 1000
METRICS_SAMPLE_INTERVAL = 60  # segundos

# ==============================================================================
# REGEX PATTERNS COMUNS
# ==============================================================================

# Padrões de validação
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
URL_PATTERN = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
IPV4_PATTERN = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

# ==============================================================================
# VERSÃO E METADADOS
# ==============================================================================

ASTRA_VERSION = "2.0.0"
ASTRA_CODENAME = "Emotional Intelligence"
AUTHOR = "António Pereira"
LICENSE = "MIT"
GITHUB_REPO = "https://github.com/Renonemre-oss/astra-assistant"
CO_AUTHOR = "Warp <agent@warp.dev>"

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def ensure_directories():
    """Cria diretórios necessários se não existirem."""
    directories = [
        DATA_DIR, LOGS_DIR, CONFIG_DIR, MODELS_DIR, CACHE_DIR,
        MEMORY_DATA_DIR, PERSONALITY_DATA_DIR, CONVERSATION_DATA_DIR,
        USER_DATA_DIR, COMPANION_DATA_DIR, VOICE_MODELS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_version_info() -> dict:
    """Retorna informações de versão."""
    return {
        'version': ASTRA_VERSION,
        'codename': ASTRA_CODENAME,
        'author': AUTHOR,
        'license': LICENSE,
        'repository': GITHUB_REPO
    }

if __name__ == "__main__":
    print(f"ASTRA {ASTRA_VERSION} - {ASTRA_CODENAME}")
    print(f"Projeto: {PROJECT_ROOT}")
    ensure_directories()
    print("✅ Diretórios verificados/criados")

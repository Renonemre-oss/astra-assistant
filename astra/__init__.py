"""
Astra AI Assistant - Assistente de IA Avançado

Um assistente de IA com capacidades multimodais incluindo:
- Reconhecimento de voz
- Síntese de fala  
- Análise contextual
- Personalidade adaptativa
- Sistema multi-usuário
- Integração com APIs externas

Autor: António Pereira
Licença: MIT
"""

__version__ = "2.0.0"
__author__ = "António Pereira"
__email__ = "antonio@astra-assistant.com"  # ✅ Corrigido: email atualizado
__description__ = "Astra AI Assistant - Assistente de IA Avançado"

# Carregar .env (DATABASE_URL, PORCUPINE_ACCESS_KEY, chaves de API, etc.)
# antes de qualquer outro módulo ler os.environ.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Compatibilidade: em Python 3.14+ o pacote 'pyaudio' ainda não tem wheel
# pré-compilado no Windows. O fork 'PyAudioWPatch' é um substituto direto
# (mesma API), mas instala-se como módulo 'pyaudiowpatch'. Isto faz
# `import pyaudio` resolver para lá em qualquer ponto do código (hotword,
# gravação de voz, SpeechRecognition) sem alterar esses módulos.
try:
    import pyaudio  # noqa: F401
except ImportError:
    try:
        import sys
        import pyaudiowpatch
        sys.modules["pyaudio"] = pyaudiowpatch
    except ImportError:
        pass

# Importações principais
# ✅ Corrigido: Imports explícitos em vez de wildcard
try:
    from .core.assistant import AssistenteGUI
    from .config.settings.main_config import CONFIG, configure_logging
except ImportError:
    # Fallback para importação absoluta
    pass

__all__ = [
    'AssistenteGUI',
    'CONFIG',
    'configure_logging',
    '__version__',
]


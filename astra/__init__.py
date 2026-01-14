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
__email__ = "your.email@example.com"
__description__ = "Astra AI Assistant - Assistente de IA Avançado"

# Importações principais
try:
    from .core.assistant import *
    from .config.settings.main_config import *
except ImportError:
    # Fallback para importação absoluta
    pass

__all__ = [
    'Assistant',
    'Config',
    '__version__',
]


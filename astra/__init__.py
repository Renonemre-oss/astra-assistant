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


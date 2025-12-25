
# Configuração de logging sem emojis para compatibilidade Windows
import logging
import sys

class SafeFormatter(logging.Formatter):
    """Formatter que remove emojis problemáticos"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Mapeamento de emojis para texto
        self.emoji_map = {
            '🔄': '[LOADING]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]',
            '🎤': '[AUDIO]',
            '🗣️': '[TTS]',
            '🎙️': '[STT]',
            '🎯': '[TARGET]',
            '🤖': '[ALEX]',
            '📊': '[INFO]',
            '🔊': '[SPEAKER]',
            '🎵': '[VOICE]',
            '🚫': '[STOP]',
            '🔐': '[SHUTDOWN]',
        }
    
    def format(self, record):
        # Aplicar formato normal
        formatted = super().format(record)
        
        # Substituir emojis problemáticos
        for emoji, replacement in self.emoji_map.items():
            formatted = formatted.replace(emoji, replacement)
        
        return formatted

def setup_safe_logging():
    """Configura logging seguro para Windows"""
    
    # Remover handlers existentes
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Criar handler com formatter seguro
    handler = logging.StreamHandler(sys.stdout)
    formatter = SafeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Configurar logger root
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(handler)
    
    return True

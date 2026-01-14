
# Patch para logging sem problemas de encoding
import logging
import sys

def setup_windows_safe_logging():
    """Configura logging seguro para Windows com emojis"""
    
    class WindowsSafeFormatter(logging.Formatter):
        """Formatter que substitui emojis por texto em Windows"""
        
        EMOJI_REPLACEMENTS = {
            '🔄': '[LOADING]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '⚠️': '[WARN]',
            '🎤': '[MIC]',
            '🗣️': '[SPEAK]',
            '🎙️': '[LISTEN]',
            '🎯': '[TARGET]',
            '🤖': '[ASTRA]',
        }
        
        def format(self, record):
            formatted = super().format(record)
            
            # Substituir emojis apenas no Windows
            if sys.platform == 'win32':
                for emoji, replacement in self.EMOJI_REPLACEMENTS.items():
                    formatted = formatted.replace(emoji, replacement)
            
            return formatted
    
    # Aplicar formatter a todos os handlers
    formatter = WindowsSafeFormatter('%(asctime)s - %(levelname)s - %(message)s')
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)
    
    return True


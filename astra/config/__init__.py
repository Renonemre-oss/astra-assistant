# Config module initialization
# ✅ Bug #14: Garantir que DATABASE_AVAILABLE seja sempre atualizado corretamente

# Importar todas as configurações do módulo config
from .settings.main_config import (
    CONFIG,
    UI_STYLES,
    PERSONALITIES,
    TESSERACT_PATHS,
    DATABASE_CONFIG_FILE,
    WORK_DIR,
    DATA_DIR,
    NEURAL_DIR,
    configure_logging,
    check_dependencies,
    get_database_available,
)

# Variáveis de estado do sistema
DATABASE_AVAILABLE = False
TESSERACT_AVAILABLE = False
DEPENDENCIES = {}

# Verificar dependências no import
try:
    DEPENDENCIES = check_dependencies()
    DATABASE_AVAILABLE = get_database_available()  # ✅ Usar função dedicada
    TESSERACT_AVAILABLE = DEPENDENCIES.get('pytesseract', False)
except Exception as e:
    import logging
    logging.warning(f"Erro ao verificar dependências: {e}")
    DEPENDENCIES = {}

def setup_tesseract():
    """Setup tesseract OCR."""
    pass

def get_database_available():
    """Get database availability."""
    return DATABASE_AVAILABLE

__all__ = [
    'CONFIG',
    'UI_STYLES', 
    'PERSONALITIES',
    'TESSERACT_PATHS',
    'DATABASE_CONFIG_FILE',
    'DATABASE_AVAILABLE',
    'TESSERACT_AVAILABLE',
    'DEPENDENCIES',
    'WORK_DIR',
    'DATA_DIR',
    'NEURAL_DIR',
    'setup_tesseract',
    'check_dependencies',
    'get_database_available'
]

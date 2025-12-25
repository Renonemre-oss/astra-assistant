# Config module initialization

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
)

# Variáveis compatíveis
DATABASE_AVAILABLE = False
TESSERACT_AVAILABLE = False
DEPENDENCIES = {}

try:
    deps = check_dependencies()
    DATABASE_AVAILABLE = deps.get('database', False)
    TESSERACT_AVAILABLE = deps.get('tesseract', False)
    DEPENDENCIES = deps
except:
    pass

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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA Assistant - Version Information
Sistema de controle de versão interno
"""

__version__ = "0.8.0-alpha"
__version_info__ = (0, 8, 0, "alpha", 0)

VERSION_MAJOR = 0
VERSION_MINOR = 8
VERSION_PATCH = 0
VERSION_STAGE = "alpha"
VERSION_BUILD = 0

# Informações da versão
VERSION_NAME = "Contextual Intelligence"
VERSION_CODENAME = "Alpha Phoenix"
RELEASE_DATE = "2025-09-26"

# Status de desenvolvimento
DEVELOPMENT_STATUS = "Alpha"
STABILITY = "Development/Testing"
API_STABILITY = "Unstable"

# Funcionalidades da versão
FEATURES = [
    "multi_user_system",
    "contextual_analysis", 
    "speech_engine",
    "database_integration",
    "voice_cloning",
    "performance_monitoring"
]

# Limitações conhecidas
KNOWN_LIMITATIONS = [
    "partial_voice_recognition",
    "sqlalchemy_conflicts",
    "dependency_version_conflicts", 
    "limited_error_handling",
    "manual_configuration_required"
]

def get_version():
    """Retorna a versão atual como string."""
    return __version__

def get_version_info():
    """Retorna informações detalhadas da versão."""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "name": VERSION_NAME,
        "codename": VERSION_CODENAME,
        "release_date": RELEASE_DATE,
        "status": DEVELOPMENT_STATUS,
        "stability": STABILITY,
        "features": FEATURES,
        "limitations": KNOWN_LIMITATIONS
    }

def is_stable():
    """Verifica se esta é uma versão estável."""
    return VERSION_STAGE in ["stable", "release", "final"]

def is_development():
    """Verifica se esta é uma versão de desenvolvimento."""
    return VERSION_STAGE in ["alpha", "beta", "dev", "rc"]

def print_version_info():
    """Imprime informações da versão de forma formatada."""
    print(f"🤖 ASTRA Assistant v{__version__}")
    print(f"📅 Release: {RELEASE_DATE}")
    print(f"🏷️  Status: {DEVELOPMENT_STATUS}")
    print(f"⚖️  Stability: {STABILITY}")
    print(f"🎯 Codename: {VERSION_CODENAME}")

if __name__ == "__main__":
    print_version_info()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA/Astra - Secrets Manager
Sistema seguro para gestão de API keys, tokens e credenciais.
"""

import os
import logging
from typing import Dict, Optional, Any, List
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
import base64

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SecretMetadata:
    """Metadados de um secret."""
    name: str
    created_at: datetime
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    is_required: bool = False


class SecretManager:
    """Gestor seguro de secrets para o ASTRA/Astra."""
    
    def __init__(self, env_file: Optional[Path] = None):
        self.env_file = env_file or Path(__file__).parent.parent.parent / '.env'
        self._secrets: Dict[str, str] = {}
        self._metadata: Dict[str, SecretMetadata] = {}
        self._cipher = None
        
        if CRYPTO_AVAILABLE:
            self._init_encryption()
        
        self._load_secrets()
        logger.info(f"✅ Secret Manager: {len(self._secrets)} secrets carregados")
    
    def _init_encryption(self):
        """Inicializa encriptação."""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'ASTRA_Astra_2024',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(b'ASTRA_master_key'))
            self._cipher = Fernet(key)
        except Exception as e:
            logger.error(f"Erro ao inicializar encriptação: {e}")
    
    def _load_secrets(self):
        """Carrega secrets do .env."""
        if DOTENV_AVAILABLE and self.env_file.exists():
            load_dotenv(self.env_file)
        
        required = ['OLLAMA_API_URL', 'DATABASE_PATH']
        optional = ['NEWSDATA_API_KEY', 'OPENWEATHER_API_KEY', 'JWT_SECRET_KEY']
        
        for name in required:
            value = os.getenv(name)
            if value:
                self._store_secret(name, value, True)
        
        for name in optional:
            value = os.getenv(name)
            if value:
                self._store_secret(name, value, False)
        
        # Defaults
        if 'OLLAMA_API_URL' not in self._secrets:
            self._store_secret('OLLAMA_API_URL', 'http://localhost:11434', True)
        if 'DATABASE_PATH' not in self._secrets:
            self._store_secret('DATABASE_PATH', 'data/Astra.db', True)
        if 'JWT_SECRET_KEY' not in self._secrets:
            import secrets
            self._store_secret('JWT_SECRET_KEY', secrets.token_urlsafe(32), True)
    
    def _store_secret(self, name: str, value: str, is_required: bool):
        """Armazena secret encriptado."""
        try:
            if self._cipher:
                encrypted = self._cipher.encrypt(value.encode()).decode()
                self._secrets[name] = encrypted
            else:
                self._secrets[name] = value
            
            self._metadata[name] = SecretMetadata(
                name=name,
                created_at=datetime.now(),
                is_required=is_required
            )
        except Exception as e:
            logger.error(f"Erro ao armazenar '{name}': {e}")
    
    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Obtém secret."""
        if name not in self._secrets:
            return default
        
        try:
            if name in self._metadata:
                self._metadata[name].last_accessed = datetime.now()
                self._metadata[name].access_count += 1
            
            value = self._secrets[name]
            if self._cipher:
                try:
                    return self._cipher.decrypt(value.encode()).decode()
                except:
                    return value
            return value
        except Exception as e:
            logger.error(f"Erro ao obter '{name}': {e}")
            return default
    
    def set(self, name: str, value: str, is_required: bool = False):
        """Define secret."""
        self._store_secret(name, value, is_required)
    
    def list_secrets(self) -> Dict[str, Dict]:
        """Lista secrets (sem valores)."""
        result = {}
        for name, meta in self._metadata.items():
            result[name] = {
                'is_required': meta.is_required,
                'access_count': meta.access_count,
                'created_at': meta.created_at.isoformat()
            }
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Status do sistema."""
        return {
            'total_secrets': len(self._secrets),
            'required': sum(1 for m in self._metadata.values() if m.is_required),
            'optional': sum(1 for m in self._metadata.values() if not m.is_required),
            'encryption_enabled': self._cipher is not None
        }


_secret_manager: Optional[SecretManager] = None

def get_secret_manager() -> SecretManager:
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = SecretManager()
    return _secret_manager

def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    return get_secret_manager().get(name, default)



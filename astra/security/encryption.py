#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA/Astra - Encryption System
Sistema de encriptação para dados sensíveis.
"""

import logging
import base64
from typing import Optional, Union

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

logger = logging.getLogger(__name__)


class DataEncryptor:
    """Encriptação de dados sensíveis."""
    
    def __init__(self, key: Optional[bytes] = None):
        if not CRYPTO_AVAILABLE:
            logger.error("❌ cryptography não instalado!")
            self._cipher = None
            return
        
        if key:
            self._key = key
        else:
            self._key = Fernet.generate_key()
        
        self._cipher = Fernet(self._key)
        logger.info("🔐 Encriptação inicializada")
    
    @classmethod
    def from_password(cls, password: str, salt: bytes = b'ASTRA_Astra_salt'):
        """Cria encriptação a partir de password."""
        if not CRYPTO_AVAILABLE:
            return cls(None)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return cls(key)
    
    def encrypt(self, data: Union[str, bytes]) -> Optional[str]:
        """Encripta dados."""
        if not self._cipher:
            return None
        
        try:
            if isinstance(data, str):
                data = data.encode()
            
            encrypted = self._cipher.encrypt(data)
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Erro ao encriptar: {e}")
            return None
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """Decripta dados."""
        if not self._cipher:
            return None
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self._cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Erro ao decriptar: {e}")
            return None
    
    def get_key(self) -> Optional[str]:
        """Retorna chave de encriptação (base64)."""
        if self._key:
            return base64.urlsafe_b64encode(self._key).decode()
        return None


_default_encryptor: Optional[DataEncryptor] = None

def get_encryptor() -> DataEncryptor:
    global _default_encryptor
    if _default_encryptor is None:
        _default_encryptor = DataEncryptor.from_password('ASTRA_default_key_2024')
    return _default_encryptor


def encrypt_data(data: Union[str, bytes]) -> Optional[str]:
    """Atalho para encriptar."""
    return get_encryptor().encrypt(data)


def decrypt_data(encrypted: str) -> Optional[str]:
    """Atalho para decriptar."""
    return get_encryptor().decrypt(encrypted)



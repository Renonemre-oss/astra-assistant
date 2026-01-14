"""
ASTRA/Astra - Security Module
Sistema completo de segurança.
"""

from .secrets_manager import SecretManager, get_secret_manager, get_secret
from .authentication import AuthenticationManager, get_auth_manager, User
from .rate_limiter import RateLimiter, get_rate_limiter, rate_limit
from .encryption import DataEncryptor, get_encryptor, encrypt_data, decrypt_data

__all__ = [
    'SecretManager',
    'get_secret_manager',
    'get_secret',
    'AuthenticationManager',
    'get_auth_manager',
    'User',
    'RateLimiter',
    'get_rate_limiter',
    'rate_limit',
    'DataEncryptor',
    'get_encryptor',
    'encrypt_data',
    'decrypt_data',
]



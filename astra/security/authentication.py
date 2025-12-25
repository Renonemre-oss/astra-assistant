#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA/Astra - Authentication System
Sistema de autenticação JWT para API REST.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

from .secrets_manager import get_secret

logger = logging.getLogger(__name__)


@dataclass
class User:
    """Usuário autenticado."""
    username: str
    role: str = "user"
    created_at: Optional[datetime] = None


class AuthenticationManager:
    """Gestor de autenticação JWT."""
    
    def __init__(self):
        self.secret_key = get_secret('JWT_SECRET_KEY', 'default_secret_key_change_me')
        self.algorithm = "HS256"
        self.access_token_expire = 60  # minutos
        self.refresh_token_expire = 7  # dias
        
        if not JWT_AVAILABLE:
            logger.warning("⚠️ PyJWT não instalado. Use: pip install pyjwt")
    
    def create_access_token(self, username: str, role: str = "user") -> Optional[str]:
        """Cria token de acesso JWT."""
        if not JWT_AVAILABLE:
            return None
        
        try:
            payload = {
                'sub': username,
                'role': role,
                'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expire),
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Erro ao criar token: {e}")
            return None
    
    def create_refresh_token(self, username: str) -> Optional[str]:
        """Cria token de refresh."""
        if not JWT_AVAILABLE:
            return None
        
        try:
            payload = {
                'sub': username,
                'exp': datetime.utcnow() + timedelta(days=self.refresh_token_expire),
                'iat': datetime.utcnow(),
                'type': 'refresh'
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Erro ao criar refresh token: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica e decodifica token."""
        if not JWT_AVAILABLE:
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token inválido: {e}")
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Obtém usuário do token."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        return User(
            username=payload.get('sub'),
            role=payload.get('role', 'user')
        )
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Renova token de acesso usando refresh token."""
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return None
        
        return self.create_access_token(
            username=payload['sub'],
            role=payload.get('role', 'user')
        )


_auth_manager: Optional[AuthenticationManager] = None

def get_auth_manager() -> AuthenticationManager:
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager()
    return _auth_manager



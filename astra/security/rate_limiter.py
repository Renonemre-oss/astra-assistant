#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/Astra - Rate Limiter
Sistema de rate limiting para proteger API contra abuse.
"""

import logging
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RateLimitRule:
    """Regra de rate limiting."""
    max_requests: int
    window_seconds: int
    name: str = "default"


class RateLimiter:
    """Rate limiter baseado em sliding window."""
    
    def __init__(self):
        # key -> deque de timestamps
        self._requests: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Regras por tipo
        self.rules = {
            'default': RateLimitRule(max_requests=60, window_seconds=60),  # 60 req/min
            'api': RateLimitRule(max_requests=100, window_seconds=60),     # 100 req/min
            'auth': RateLimitRule(max_requests=5, window_seconds=60),      # 5 req/min
            'strict': RateLimitRule(max_requests=10, window_seconds=60),   # 10 req/min
        }
    
    def _clean_old_requests(self, key: str, window_seconds: int):
        """Remove requisições antigas da janela."""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Remove timestamps antigos
        while self._requests[key] and self._requests[key][0] < cutoff_time:
            self._requests[key].popleft()
    
    def is_allowed(self, key: str, rule_name: str = 'default') -> Tuple[bool, Optional[int]]:
        """
        Verifica se requisição é permitida.
        
        Args:
            key: Identificador (IP, user, etc)
            rule_name: Nome da regra a aplicar
            
        Returns:
            (allowed, retry_after_seconds)
        """
        rule = self.rules.get(rule_name, self.rules['default'])
        
        # Limpar requisições antigas
        self._clean_old_requests(key, rule.window_seconds)
        
        # Verificar limite
        current_requests = len(self._requests[key])
        
        if current_requests >= rule.max_requests:
            # Calcular tempo até próxima janela
            oldest_request = self._requests[key][0]
            retry_after = int(rule.window_seconds - (time.time() - oldest_request)) + 1
            
            logger.warning(f"🚫 Rate limit atingido: {key} [{rule_name}]")
            return False, retry_after
        
        # Permitir requisição
        self._requests[key].append(time.time())
        return True, None
    
    def get_remaining(self, key: str, rule_name: str = 'default') -> int:
        """Retorna requisições restantes."""
        rule = self.rules.get(rule_name, self.rules['default'])
        self._clean_old_requests(key, rule.window_seconds)
        
        current_requests = len(self._requests[key])
        return max(0, rule.max_requests - current_requests)
    
    def reset(self, key: str):
        """Reseta contadores para uma chave."""
        if key in self._requests:
            del self._requests[key]
    
    def get_stats(self) -> Dict:
        """Estatísticas de uso."""
        return {
            'active_keys': len(self._requests),
            'total_requests_tracked': sum(len(reqs) for reqs in self._requests.values()),
            'rules': {name: {'max': rule.max_requests, 'window': rule.window_seconds} 
                     for name, rule in self.rules.items()}
        }


_rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def rate_limit(key: str, rule: str = 'default') -> Tuple[bool, Optional[int]]:
    """Atalho para verificar rate limit."""
    return get_rate_limiter().is_allowed(key, rule)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/Astra - Smart Cache System
Sistema de cache inteligente com Redis e fallback local.
"""

import logging
import pickle
import hashlib
import time
from typing import Any, Optional, Callable
from functools import wraps
from pathlib import Path

logger = logging.getLogger(__name__)

# Tentar importar Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("⚠️ Redis não disponível - usando cache local")

# Tentar importar diskcache
try:
    import diskcache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False
    logger.warning("⚠️ diskcache não disponível - cache limitado")


class SmartCache:
    """Sistema de cache híbrido (Redis + Local)."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        local_cache_dir: Optional[Path] = None,
        default_ttl: int = 3600
    ):
        """
        Inicializa sistema de cache.
        
        Args:
            redis_url: URL do Redis
            local_cache_dir: Diretório para cache local
            default_ttl: Tempo de vida padrão (segundos)
        """
        self.default_ttl = default_ttl
        self.redis_client = None
        self.local_cache = None
        self.memory_cache = {}
        
        # Tentar conectar Redis
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=False,
                    socket_connect_timeout=2
                )
                # Testar conexão
                self.redis_client.ping()
                logger.info("✅ Redis cache conectado")
            except Exception as e:
                logger.warning(f"⚠️ Redis não disponível: {e}")
                self.redis_client = None
        
        # Configurar cache local
        if DISKCACHE_AVAILABLE:
            if local_cache_dir is None:
                local_cache_dir = Path(__file__).parent.parent.parent / 'data' / 'cache'
            
            local_cache_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                self.local_cache = diskcache.Cache(str(local_cache_dir))
                logger.info("✅ Cache local (diskcache) ativo")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao inicializar cache local: {e}")
                self.local_cache = None
        
        # Log do sistema ativo
        if self.redis_client:
            logger.info("🚀 Cache: Redis (primário) + Local (secundário)")
        elif self.local_cache:
            logger.info("💾 Cache: Local (diskcache)")
        else:
            logger.info("🧠 Cache: Memória apenas")
    
    def _make_key(self, key: str, prefix: str = "Astra") -> str:
        """Cria chave de cache com prefixo."""
        return f"{prefix}:{key}"
    
    def _hash_key(self, *args, **kwargs) -> str:
        """Gera hash de argumentos para usar como chave."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor do cache.
        
        Args:
            key: Chave do cache
            default: Valor padrão se não encontrado
            
        Returns:
            Valor armazenado ou default
        """
        full_key = self._make_key(key)
        
        # 1. Tentar memória (mais rápido)
        if full_key in self.memory_cache:
            value, expiry = self.memory_cache[full_key]
            if expiry > time.time():
                logger.debug(f"💾 Cache hit (memory): {key}")
                return value
            else:
                del self.memory_cache[full_key]
        
        # 2. Tentar Redis
        if self.redis_client:
            try:
                value = self.redis_client.get(full_key)
                if value is not None:
                    logger.debug(f"🔴 Cache hit (Redis): {key}")
                    result = pickle.loads(value)
                    # Armazenar em memória para próximas leituras
                    self.memory_cache[full_key] = (result, time.time() + 300)
                    return result
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler Redis: {e}")
        
        # 3. Tentar cache local
        if self.local_cache:
            try:
                value = self.local_cache.get(full_key)
                if value is not None:
                    logger.debug(f"💿 Cache hit (local): {key}")
                    # Armazenar em memória
                    self.memory_cache[full_key] = (value, time.time() + 300)
                    return value
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler cache local: {e}")
        
        logger.debug(f"❌ Cache miss: {key}")
        return default
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Armazena valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: Tempo de vida (segundos)
            
        Returns:
            True se armazenado com sucesso
        """
        if ttl is None:
            ttl = self.default_ttl
        
        full_key = self._make_key(key)
        success = False
        
        # 1. Armazenar em memória
        self.memory_cache[full_key] = (value, time.time() + ttl)
        
        # 2. Armazenar em Redis
        if self.redis_client:
            try:
                serialized = pickle.dumps(value)
                self.redis_client.setex(full_key, ttl, serialized)
                logger.debug(f"🔴 Cache set (Redis): {key}")
                success = True
            except Exception as e:
                logger.warning(f"⚠️ Erro ao escrever Redis: {e}")
        
        # 3. Armazenar em cache local
        if self.local_cache:
            try:
                self.local_cache.set(full_key, value, expire=ttl)
                logger.debug(f"💿 Cache set (local): {key}")
                success = True
            except Exception as e:
                logger.warning(f"⚠️ Erro ao escrever cache local: {e}")
        
        return success
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache."""
        full_key = self._make_key(key)
        
        # Remover de memória
        self.memory_cache.pop(full_key, None)
        
        # Remover de Redis
        if self.redis_client:
            try:
                self.redis_client.delete(full_key)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao deletar Redis: {e}")
        
        # Remover de cache local
        if self.local_cache:
            try:
                self.local_cache.delete(full_key)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao deletar cache local: {e}")
        
        return True
    
    def clear(self, pattern: str = "*") -> int:
        """
        Limpa cache com padrão.
        
        Args:
            pattern: Padrão de chaves (* para todas)
            
        Returns:
            Número de chaves removidas
        """
        count = 0
        
        # Limpar memória
        if pattern == "*":
            count += len(self.memory_cache)
            self.memory_cache.clear()
        else:
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
            count += len(keys_to_remove)
        
        # Limpar Redis
        if self.redis_client:
            try:
                full_pattern = self._make_key(pattern)
                keys = self.redis_client.keys(full_pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    count += len(keys)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao limpar Redis: {e}")
        
        # Limpar cache local
        if self.local_cache:
            try:
                self.local_cache.clear()
                logger.info("💿 Cache local limpo")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao limpar cache local: {e}")
        
        logger.info(f"🧹 Cache limpo: {count} chaves removidas")
        return count
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do cache."""
        stats = {
            'redis_available': self.redis_client is not None,
            'local_cache_available': self.local_cache is not None,
            'memory_cache_size': len(self.memory_cache),
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info('stats')
                stats['redis_keys'] = self.redis_client.dbsize()
                stats['redis_hits'] = info.get('keyspace_hits', 0)
                stats['redis_misses'] = info.get('keyspace_misses', 0)
            except:
                pass
        
        if self.local_cache:
            try:
                stats['local_cache_size'] = len(self.local_cache)
            except:
                pass
        
        return stats


# Instância global
_smart_cache: Optional[SmartCache] = None


def get_smart_cache() -> SmartCache:
    """Obtém instância global do cache."""
    global _smart_cache
    if _smart_cache is None:
        _smart_cache = SmartCache()
    return _smart_cache


def cached(ttl: int = 3600, key_prefix: str = "func"):
    """
    Decorador para cache de funções.
    
    Args:
        ttl: Tempo de vida do cache (segundos)
        key_prefix: Prefixo da chave
        
    Example:
        @cached(ttl=600, key_prefix="embeddings")
        def generate_embedding(text):
            return expensive_computation(text)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_smart_cache()
            
            # Gerar chave baseada em argumentos
            cache_key = f"{key_prefix}:{func.__name__}:{cache._hash_key(*args, **kwargs)}"
            
            # Tentar obter do cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executar função
            result = func(*args, **kwargs)
            
            # Armazenar no cache
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra AI Assistant - AI Engine
Motor principal de IA que gerencia múltiplos provedores, fallback e cache.
"""

import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Iterator
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from .ai_providers import (
    AIProviderBase,
    AIResponse,
    ProviderStatus,
    OllamaProvider,
    OpenAIProvider
)

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada do cache de respostas."""
    prompt: str
    response: str
    provider: str
    model: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def is_expired(self, ttl_seconds: int) -> bool:
        """Verifica se a entrada expirou."""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > ttl_seconds


class AIEngine:
    """
    Motor principal de IA do Astra.
    
    Responsável por:
    - Gerenciar múltiplos provedores de IA
    - Implementar fallback automático entre provedores
    - Cachear respostas para queries similares
    - Fornecer interface unificada independente do provedor
    """
    
    # Mapeamento de provedores disponíveis
    AVAILABLE_PROVIDERS = {
        'ollama': OllamaProvider,
        'openai': OpenAIProvider,
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o AI Engine.
        
        Args:
            config: Configuração contendo:
                - default_provider: Provedor padrão a usar
                - providers: Dicionário com configurações de cada provedor
                - fallback_chain: Lista ordenada de provedores para fallback
                - cache_enabled: Se o cache está ativo
                - cache_ttl: Tempo de vida do cache em segundos
                - cache_dir: Diretório para cache persistente
        """
        self.config = config
        self.providers: Dict[str, AIProviderBase] = {}
        self.default_provider = config.get('default_provider', 'ollama')
        self.fallback_chain = config.get('fallback_chain', ['ollama'])
        
        # Configuração de cache
        self.cache_enabled = config.get('cache_enabled', True)
        self.cache_ttl = config.get('cache_ttl', 3600)  # 1 hora
        self.cache_dir = Path(config.get('cache_dir', 'data/ai_cache'))
        self.cache: Dict[str, CacheEntry] = {}
        
        # Estatísticas
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'provider_usage': {},
            'fallback_count': 0,
            'errors': 0
        }
        
        # Inicializar provedores
        self._init_providers()
        
        # Carregar cache persistente
        if self.cache_enabled:
            self._load_cache()
        
        logger.info(f"AI Engine inicializado. Provedor padrão: {self.default_provider}")
    
    def _init_providers(self):
        """Inicializa os provedores configurados."""
        providers_config = self.config.get('providers', {})
        
        for provider_name, provider_config in providers_config.items():
            if not provider_config.get('enabled', False):
                logger.info(f"Provedor {provider_name} desabilitado")
                continue
            
            if provider_name not in self.AVAILABLE_PROVIDERS:
                logger.warning(f"Provedor desconhecido: {provider_name}")
                continue
            
            try:
                provider_class = self.AVAILABLE_PROVIDERS[provider_name]
                provider = provider_class(provider_config)
                self.providers[provider_name] = provider
                
                logger.info(
                    f"Provedor {provider_name} inicializado. "
                    f"Status: {provider.get_status().value}"
                )
                
                # Inicializar estatísticas
                self.stats['provider_usage'][provider_name] = 0
                
            except Exception as e:
                logger.error(f"Erro ao inicializar provedor {provider_name}: {e}")
    
    def _get_cache_key(self, prompt: str, provider: str = None) -> str:
        """Gera chave única para cache baseada no prompt."""
        content = f"{provider or 'any'}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_cache(self, prompt: str, provider: str = None) -> Optional[AIResponse]:
        """Verifica se existe resposta em cache."""
        if not self.cache_enabled:
            return None
        
        cache_key = self._get_cache_key(prompt, provider)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            if not entry.is_expired(self.cache_ttl):
                self.stats['cache_hits'] += 1
                logger.info(f"Cache hit para prompt: {prompt[:50]}...")
                
                return AIResponse(
                    content=entry.response,
                    provider=entry.provider,
                    model=entry.model,
                    metadata={**entry.metadata, 'from_cache': True}
                )
            else:
                # Remover entrada expirada
                del self.cache[cache_key]
        
        self.stats['cache_misses'] += 1
        return None
    
    def _save_to_cache(self, prompt: str, response: AIResponse):
        """Salva resposta no cache."""
        if not self.cache_enabled or not response.success:
            return
        
        cache_key = self._get_cache_key(prompt, response.provider)
        
        entry = CacheEntry(
            prompt=prompt,
            response=response.content,
            provider=response.provider,
            model=response.model,
            timestamp=datetime.now(),
            metadata=response.metadata
        )
        
        self.cache[cache_key] = entry
        logger.debug(f"Resposta salva no cache: {cache_key}")
    
    def _load_cache(self):
        """Carrega cache persistente do disco."""
        try:
            cache_file = self.cache_dir / "cache.json"
            
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for key, entry_dict in data.items():
                    # Converter timestamp string de volta para datetime
                    entry_dict['timestamp'] = datetime.fromisoformat(entry_dict['timestamp'])
                    entry = CacheEntry(**entry_dict)
                    
                    # Apenas adicionar se não estiver expirado
                    if not entry.is_expired(self.cache_ttl):
                        self.cache[key] = entry
                
                logger.info(f"Cache carregado: {len(self.cache)} entradas")
        
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {e}")
    
    def _persist_cache(self):
        """Persiste cache no disco."""
        if not self.cache_enabled:
            return
        
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = self.cache_dir / "cache.json"
            
            # Converter para formato serializável
            data = {}
            for key, entry in self.cache.items():
                entry_dict = asdict(entry)
                entry_dict['timestamp'] = entry.timestamp.isoformat()
                data[key] = entry_dict
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Cache persistido: {len(data)} entradas")
        
        except Exception as e:
            logger.error(f"Erro ao persistir cache: {e}")
    
    def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        use_cache: bool = True,
        **kwargs
    ) -> AIResponse:
        """
        Gera uma resposta usando o AI Engine.
        
        Args:
            prompt: Prompt do usuário
            provider: Provedor específico a usar (ou None para usar padrão)
            system_prompt: Contexto/instruções do sistema
            temperature: Aleatoriedade da resposta
            use_cache: Se deve usar cache
            **kwargs: Parâmetros adicionais
            
        Returns:
            AIResponse: Resposta gerada
        """
        self.stats['total_requests'] += 1
        
        # Verificar cache primeiro
        if use_cache:
            cached_response = self._check_cache(prompt, provider)
            if cached_response:
                return cached_response
        
        # Determinar qual provedor usar
        target_provider = provider or self.default_provider
        
        # Tentar provedor especificado
        if target_provider in self.providers:
            response = self._try_provider(
                target_provider,
                prompt,
                system_prompt,
                temperature,
                **kwargs
            )
            
            if response.success:
                self._save_to_cache(prompt, response)
                self._persist_cache()
                return response
        
        # Se falhou, tentar fallback
        logger.warning(f"Provedor {target_provider} falhou, tentando fallback")
        self.stats['fallback_count'] += 1
        
        for fallback_provider in self.fallback_chain:
            if fallback_provider == target_provider:
                continue  # Já tentamos este
            
            if fallback_provider not in self.providers:
                continue
            
            logger.info(f"Tentando fallback: {fallback_provider}")
            
            response = self._try_provider(
                fallback_provider,
                prompt,
                system_prompt,
                temperature,
                **kwargs
            )
            
            if response.success:
                response.metadata['is_fallback'] = True
                response.metadata['original_provider'] = target_provider
                self._save_to_cache(prompt, response)
                self._persist_cache()
                return response
        
        # Todos os provedores falharam
        self.stats['errors'] += 1
        logger.error("Todos os provedores falharam")
        
        return AIResponse(
            content="",
            provider="none",
            model="none",
            error="Todos os provedores de IA falharam"
        )
    
    def _try_provider(
        self,
        provider_name: str,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        **kwargs
    ) -> AIResponse:
        """Tenta gerar resposta com um provedor específico."""
        provider = self.providers.get(provider_name)
        
        if not provider:
            return AIResponse(
                content="",
                provider=provider_name,
                model="unknown",
                error=f"Provedor {provider_name} não encontrado"
            )
        
        try:
            response = provider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                **kwargs
            )
            
            if response.success:
                self.stats['provider_usage'][provider_name] += 1
            
            return response
        
        except Exception as e:
            logger.error(f"Erro ao usar provedor {provider_name}: {e}")
            return AIResponse(
                content="",
                provider=provider_name,
                model="unknown",
                error=str(e)
            )
    
    def generate_stream(
        self,
        prompt: str,
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Iterator[str]:
        """
        Gera resposta em modo streaming.
        
        Args:
            prompt: Prompt do usuário
            provider: Provedor específico
            system_prompt: Contexto do sistema
            temperature: Aleatoriedade
            **kwargs: Parâmetros adicionais
            
        Yields:
            str: Chunks da resposta
        """
        target_provider = provider or self.default_provider
        
        if target_provider not in self.providers:
            yield f"[Erro: Provedor {target_provider} não disponível]"
            return
        
        provider_obj = self.providers[target_provider]
        
        try:
            for chunk in provider_obj.generate_stream(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                **kwargs
            ):
                yield chunk
        
        except Exception as e:
            logger.error(f"Erro no streaming: {e}")
            yield f"[Erro: {str(e)}]"
    
    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis."""
        return [
            name for name, provider in self.providers.items()
            if provider.get_status() == ProviderStatus.AVAILABLE
        ]
    
    def get_provider_status(self, provider_name: str) -> Optional[ProviderStatus]:
        """Retorna status de um provedor específico."""
        provider = self.providers.get(provider_name)
        return provider.get_status() if provider else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso do AI Engine."""
        return {
            **self.stats,
            'cache_size': len(self.cache),
            'cache_hit_rate': (
                self.stats['cache_hits'] / 
                (self.stats['cache_hits'] + self.stats['cache_misses'])
                if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0
                else 0.0
            ),
            'available_providers': self.get_available_providers()
        }
    
    def clear_cache(self):
        """Limpa o cache de respostas."""
        self.cache.clear()
        logger.info("Cache limpo")
        
        # Remover arquivo de cache
        try:
            cache_file = self.cache_dir / "cache.json"
            if cache_file.exists():
                cache_file.unlink()
        except Exception as e:
            logger.error(f"Erro ao remover arquivo de cache: {e}")
    
    def reload_providers(self):
        """Recarrega todos os provedores."""
        logger.info("Recarregando provedores...")
        self.providers.clear()
        self._init_providers()
    
    def __del__(self):
        """Destrutor: persiste cache antes de finalizar."""
        if self.cache_enabled and self.cache:
            self._persist_cache()


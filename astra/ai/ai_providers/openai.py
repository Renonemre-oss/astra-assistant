#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra AI Assistant - OpenAI Provider
Provedor para modelos OpenAI (GPT-3.5, GPT-4, etc).
"""

import os
from typing import Dict, List, Optional, Any, Iterator
import logging

from .base import AIProviderBase, AIResponse, ProviderStatus

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProviderBase):
    """
    Provedor de IA para OpenAI API.
    
    Suporta modelos OpenAI como:
    - gpt-4
    - gpt-3.5-turbo
    - gpt-4-turbo
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o provedor OpenAI.
        
        Args:
            config: Configuração contendo:
                - api_key: Chave da API OpenAI (ou variável de ambiente OPENAI_API_KEY)
                - model: Modelo a usar (padrão: gpt-3.5-turbo)
                - timeout: Timeout em segundos (padrão: 60)
                - max_retries: Tentativas máximas (padrão: 3)
        """
        super().__init__(config)
        
        # Tentar obter API key
        self.api_key = self.get_config('api_key') or os.getenv('OPENAI_API_KEY')
        self.model = self.get_config('model', 'gpt-3.5-turbo')
        self.timeout = self.get_config('timeout', 60)
        self.max_retries = self.get_config('max_retries', 3)
        
        # Cliente OpenAI (importado dinamicamente)
        self.client = None
        
        if not self.api_key:
            self.set_status(
                ProviderStatus.UNAVAILABLE,
                "API key não configurada para OpenAI"
            )
        else:
            # Tentar importar e inicializar cliente
            if self._init_client():
                self.set_status(ProviderStatus.AVAILABLE)
            else:
                self.set_status(
                    ProviderStatus.UNAVAILABLE,
                    "Biblioteca OpenAI não instalada"
                )
    
    def _init_client(self) -> bool:
        """
        Inicializa o cliente OpenAI.
        
        Returns:
            bool: True se inicializado com sucesso
        """
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info("Cliente OpenAI inicializado")
            return True
        except ImportError:
            logger.warning(
                "Biblioteca 'openai' não instalada. "
                "Instale com: pip install openai"
            )
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente OpenAI: {e}")
            return False
    
    def check_availability(self) -> bool:
        """
        Verifica se o OpenAI está disponível.
        
        Returns:
            bool: True se disponível
        """
        if not self.client or not self.api_key:
            return False
        
        try:
            # Tenta listar modelos como teste
            models = self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade OpenAI: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        Lista modelos disponíveis na API OpenAI.
        
        Returns:
            List[str]: Lista de modelos
        """
        if not self.client:
            return []
        
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Erro ao listar modelos OpenAI: {e}")
            return []
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> AIResponse:
        """
        Gera resposta usando OpenAI.
        
        Args:
            prompt: Prompt do usuário
            system_prompt: Instruções do sistema
            temperature: Aleatoriedade (0.0 - 2.0)
            max_tokens: Máximo de tokens
            stop_sequences: Sequências de parada
            **kwargs: Parâmetros adicionais
            
        Returns:
            AIResponse: Resposta do modelo
        """
        if not self.client:
            return AIResponse(
                content="",
                provider="openai",
                model=self.model,
                error="Cliente OpenAI não inicializado"
            )
        
        if not prompt or not prompt.strip():
            return AIResponse(
                content="",
                provider="openai",
                model=self.model,
                error="Prompt vazio"
            )
        
        # Construir mensagens
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Adicionar ao histórico
        self.add_to_history("user", prompt)
        
        try:
            # Preparar parâmetros
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            if stop_sequences:
                params["stop"] = stop_sequences
            
            # Fazer chamada
            response = self.client.chat.completions.create(**params)
            
            # Extrair resposta
            content = response.choices[0].message.content
            
            # Adicionar ao histórico
            self.add_to_history("assistant", content)
            
            # Atualizar status
            self.set_status(ProviderStatus.AVAILABLE)
            
            return AIResponse(
                content=content,
                provider="openai",
                model=self.model,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'model': response.model,
                }
            )
            
        except Exception as e:
            error_msg = f"Erro OpenAI: {str(e)}"
            logger.error(error_msg)
            self.set_status(ProviderStatus.ERROR, error_msg)
            
            return AIResponse(
                content="",
                provider="openai",
                model=self.model,
                error=error_msg
            )
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Gera resposta em modo streaming.
        
        Args:
            prompt: Prompt do usuário
            system_prompt: Instruções do sistema
            temperature: Aleatoriedade
            max_tokens: Máximo de tokens
            **kwargs: Parâmetros adicionais
            
        Yields:
            str: Chunks da resposta
        """
        if not self.client:
            yield "[Erro: Cliente OpenAI não inicializado]"
            return
        
        if not prompt or not prompt.strip():
            yield ""
            return
        
        # Construir mensagens
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Adicionar ao histórico
        self.add_to_history("user", prompt)
        
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": True
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            response = self.client.chat.completions.create(**params)
            
            full_response = ""
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Adicionar ao histórico
            if full_response:
                self.add_to_history("assistant", full_response)
            
            self.set_status(ProviderStatus.AVAILABLE)
            
        except Exception as e:
            error_msg = f"Erro streaming OpenAI: {str(e)}"
            logger.error(error_msg)
            self.set_status(ProviderStatus.ERROR, error_msg)
            yield f"[Erro: {error_msg}]"


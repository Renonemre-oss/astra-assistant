#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra AI Assistant - Ollama Provider
Provedor para modelos de IA local via Ollama.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any, Iterator
import logging

from .base import AIProviderBase, AIResponse, ProviderStatus

logger = logging.getLogger(__name__)


class OllamaProvider(AIProviderBase):
    """
    Provedor de IA para Ollama (modelos locais).
    
    Suporta qualquer modelo Ollama instalado localmente, como:
    - llama3.2
    - mistral
    - codellama
    - phi
    - etc.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o provedor Ollama.
        
        Args:
            config: Configuração contendo:
                - url: URL do servidor Ollama (padrão: http://localhost:11434)
                - model: Nome do modelo a usar (padrão: llama3.2)
                - timeout: Timeout em segundos (padrão: 60)
                - max_retries: Número máximo de tentativas (padrão: 3)
        """
        super().__init__(config)
        
        self.url = self.get_config('url', 'http://localhost:11434')
        self.model = self.get_config('model', 'llama3.2')
        self.timeout = self.get_config('timeout', 60)
        self.max_retries = self.get_config('max_retries', 3)
        
        # Verifica disponibilidade inicial
        if self.check_availability():
            self.set_status(ProviderStatus.AVAILABLE)
        else:
            self.set_status(ProviderStatus.UNAVAILABLE, "Ollama não está acessível")
    
    def check_availability(self) -> bool:
        """
        Verifica se o Ollama está rodando e acessível.
        
        Returns:
            bool: True se disponível
        """
        try:
            response = requests.get(f"{self.url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                
                # Verifica se o modelo configurado está disponível
                model_names = [m.get('name', '') for m in models]
                if self.model not in model_names:
                    logger.warning(
                        f"Modelo '{self.model}' não encontrado. "
                        f"Modelos disponíveis: {', '.join(model_names)}"
                    )
                    return False
                
                logger.info(f"Ollama disponível com modelo: {self.model}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade do Ollama: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        Lista todos os modelos disponíveis no Ollama.
        
        Returns:
            List[str]: Lista de nomes de modelos
        """
        try:
            response = requests.get(f"{self.url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m.get('name', '') for m in models]
            return []
        except Exception as e:
            logger.error(f"Erro ao listar modelos Ollama: {e}")
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
        Gera uma resposta usando o Ollama.
        
        Args:
            prompt: Prompt do usuário
            system_prompt: Contexto/instruções do sistema
            temperature: Aleatoriedade (0.0 - 1.0)
            max_tokens: Máximo de tokens (não suportado diretamente pelo Ollama)
            stop_sequences: Sequências de parada
            **kwargs: Parâmetros adicionais específicos do Ollama
            
        Returns:
            AIResponse: Resposta do modelo
        """
        if not prompt or not prompt.strip():
            return AIResponse(
                content="",
                provider="ollama",
                model=self.model,
                error="Prompt vazio"
            )
        
        # Construir o prompt completo
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Adicionar ao histórico
        self.add_to_history("user", prompt)
        
        # Tentar gerar resposta
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Tentativa {attempt + 1}/{self.max_retries}")
                    time.sleep(1)
                
                # Preparar payload
                payload = {
                    "model": self.model,
                    "prompt": full_prompt.strip(),
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    }
                }
                
                # Adicionar stop sequences se fornecidas
                if stop_sequences:
                    payload["options"]["stop"] = stop_sequences
                
                # Fazer requisição
                response = requests.post(
                    f"{self.url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                # Verificar resposta
                if response.status_code == 404:
                    error_msg = f"Modelo '{self.model}' não encontrado"
                    self.set_status(ProviderStatus.ERROR, error_msg)
                    return AIResponse(
                        content="",
                        provider="ollama",
                        model=self.model,
                        error=error_msg
                    )
                
                response.raise_for_status()
                data = response.json()
                
                # Extrair resposta
                content = data.get('response', '').strip()
                
                if not content:
                    raise ValueError("Resposta vazia do Ollama")
                
                # Adicionar ao histórico
                self.add_to_history("assistant", content)
                
                # Atualizar status
                self.set_status(ProviderStatus.AVAILABLE)
                
                # Retornar resposta
                return AIResponse(
                    content=content,
                    provider="ollama",
                    model=self.model,
                    tokens_used=data.get('eval_count'),
                    finish_reason=data.get('done_reason'),
                    metadata={
                        'total_duration': data.get('total_duration'),
                        'load_duration': data.get('load_duration'),
                        'prompt_eval_count': data.get('prompt_eval_count'),
                        'eval_count': data.get('eval_count'),
                    }
                )
                
            except requests.exceptions.Timeout:
                error_msg = "Timeout ao aguardar resposta do Ollama"
                logger.error(f"{error_msg} (tentativa {attempt + 1})")
                if attempt == self.max_retries - 1:
                    self.set_status(ProviderStatus.ERROR, error_msg)
                    return AIResponse(
                        content="",
                        provider="ollama",
                        model=self.model,
                        error=error_msg
                    )
            
            except requests.exceptions.ConnectionError:
                error_msg = "Erro de conexão com Ollama"
                logger.error(f"{error_msg} (tentativa {attempt + 1})")
                if attempt == self.max_retries - 1:
                    self.set_status(ProviderStatus.UNAVAILABLE, error_msg)
                    return AIResponse(
                        content="",
                        provider="ollama",
                        model=self.model,
                        error=error_msg
                    )
            
            except Exception as e:
                error_msg = f"Erro inesperado: {str(e)}"
                logger.error(f"{error_msg} (tentativa {attempt + 1})")
                if attempt == self.max_retries - 1:
                    self.set_status(ProviderStatus.ERROR, error_msg)
                    return AIResponse(
                        content="",
                        provider="ollama",
                        model=self.model,
                        error=error_msg
                    )
        
        # Se chegou aqui, todas as tentativas falharam
        error_msg = "Todas as tentativas falharam"
        self.set_status(ProviderStatus.ERROR, error_msg)
        return AIResponse(
            content="",
            provider="ollama",
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
        Gera uma resposta em modo streaming.
        
        Args:
            prompt: Prompt do usuário
            system_prompt: Contexto do sistema
            temperature: Aleatoriedade
            max_tokens: Máximo de tokens (não suportado)
            **kwargs: Parâmetros adicionais
            
        Yields:
            str: Chunks da resposta
        """
        if not prompt or not prompt.strip():
            yield ""
            return
        
        # Construir prompt completo
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Adicionar ao histórico
        self.add_to_history("user", prompt)
        
        try:
            payload = {
                "model": self.model,
                "prompt": full_prompt.strip(),
                "stream": True,
                "options": {
                    "temperature": temperature,
                }
            }
            
            response = requests.post(
                f"{self.url}/api/generate",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        chunk = data.get('response', '')
                        if chunk:
                            full_response += chunk
                            yield chunk
                        
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        logger.warning("Linha JSON inválida recebida")
                        continue
            
            # Adicionar resposta completa ao histórico
            if full_response:
                self.add_to_history("assistant", full_response)
            
            self.set_status(ProviderStatus.AVAILABLE)
            
        except Exception as e:
            error_msg = f"Erro no streaming: {str(e)}"
            logger.error(error_msg)
            self.set_status(ProviderStatus.ERROR, error_msg)
            yield f"[Erro: {error_msg}]"


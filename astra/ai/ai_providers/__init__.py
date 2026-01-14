#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra AI Assistant - AI Providers
Provedores de IA disponíveis para o Astra.
"""

from .base import AIProviderBase, AIResponse, AIMessage, ProviderStatus
from .ollama import OllamaProvider
from .openai import OpenAIProvider

__all__ = [
    'AIProviderBase',
    'AIResponse',
    'AIMessage',
    'ProviderStatus',
    'OllamaProvider',
    'OpenAIProvider',
]


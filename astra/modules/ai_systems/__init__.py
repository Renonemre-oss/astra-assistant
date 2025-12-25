#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra - AI Systems Module
Módulo de sistemas de IA avançada incluindo:
- Análise comportamental
- Previsão de necessidades  
- NLP avançado
- Reconhecimento de emoções
- Sistema de recomendações
"""

from .behavioral_analyzer import BehavioralAnalyzer
from .needs_predictor import NeedsPredictor
from .advanced_nlp import AdvancedNLP
from .emotion_recognizer import EmotionRecognizer
from .recommendation_engine import RecommendationEngine
from .ai_manager import AIManager

__all__ = [
    'BehavioralAnalyzer',
    'NeedsPredictor', 
    'AdvancedNLP',
    'EmotionRecognizer',
    'RecommendationEngine',
    'AIManager'
]

__version__ = "1.0.0"
__author__ = "Astra AI Assistant"

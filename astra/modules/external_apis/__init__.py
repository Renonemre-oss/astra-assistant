#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Assistente Pessoal Inteligente
Módulo de Integração com APIs Externas

Este módulo centraliza todas as integrações com APIs externas, incluindo:
- Weather APIs (OpenWeatherMap, AccuWeather)
- News APIs (NewsAPI, RSS feeds)
- Calendar APIs (Google Calendar, Outlook)
- Email APIs (Gmail, Outlook)
- Social Media APIs (notificações básicas)
"""

from .base_api import BaseAPI
from .weather_api import WeatherAPI
from .news_api import NewsAPI
from .calendar_api import CalendarAPI
from .email_api import EmailAPI
from .social_api import SocialMediaAPI
from .api_manager import APIManager

__all__ = [
    'BaseAPI',
    'WeatherAPI',
    'NewsAPI',
    'CalendarAPI',
    'EmailAPI',
    'SocialMediaAPI',
    'APIManager'
]

__version__ = "1.0.0"
__author__ = "ASTRA Assistant"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
APIManager - Orquestrador central para integrações externas.
Fornece uma fachada simples sobre News, Calendar, Email e Social.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .news_api import NewsAPI
from .weather_api import WeatherAPI as WeatherExternal
from .calendar_api import CalendarAPI
from .email_api import EmailAPI
from .social_api import SocialMediaAPI


class APIManager:
    def __init__(self):
        # Instâncias preguiçosas (lazy)
        self._news: Optional[NewsAPI] = None
        self._weather: Optional[WeatherExternal] = None
        self._calendar: Optional[CalendarAPI] = None
        self._email: Optional[EmailAPI] = None
        self._social: Optional[SocialMediaAPI] = None

    # ---------- News ----------
    @property
    def news(self) -> NewsAPI:
        if self._news is None:
            provider = os.getenv("NEWS_PROVIDER", "newsdata")
            self._news = NewsAPI(provider=provider)
        return self._news

    # ---------- Weather ----------
    @property
    def weather(self) -> WeatherExternal:
        if self._weather is None:
            provider = os.getenv("WEATHER_PROVIDER", "openweathermap")
            api_key = os.getenv("OPENWEATHER_API_KEY", "")
            self._weather = WeatherExternal(provider=provider, api_key=api_key, language=os.getenv("WEATHER_LANG", "pt_br"))
        return self._weather

    # ---------- Calendar ----------
    @property
    def calendar(self) -> CalendarAPI:
        if self._calendar is None:
            self._calendar = CalendarAPI()
        return self._calendar

    # ---------- Email ----------
    @property
    def email(self) -> EmailAPI:
        if self._email is None:
            self._email = EmailAPI()
        return self._email

    # ---------- Social ----------
    @property
    def social(self) -> SocialMediaAPI:
        if self._social is None:
            self._social = SocialMediaAPI()
        return self._social

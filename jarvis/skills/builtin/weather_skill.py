#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Astra AI Assistant - Weather Skill
Skill para obter previsão do tempo.
"""

import re
import requests
from typing import Dict, Any
import logging

from ..base_skill import BaseSkill, SkillMetadata, SkillResponse, SkillPriority, SkillStatus

logger = logging.getLogger(__name__)


class WeatherSkill(BaseSkill):
    """
    Skill para obter informações sobre o clima.
    
    Funcionalidades:
    - Clima atual para uma cidade
    - Previsão para os próximos dias
    - Suporta OpenWeatherMap API
    """
    
    def get_metadata(self) -> SkillMetadata:
        """Retorna metadados da skill."""
        return SkillMetadata(
            name="Weather",
            version="1.0.0",
            description="Obt\u00e9m informa\u00e7\u00f5es sobre clima e previs\u00e3o do tempo",
            author="Astra Team",
            dependencies=["requests"],
            requires_api_keys=["openweather_api_key"],
            keywords=[
                "clima", "tempo", "temperatura", "previsão",
                "weather", "forecast", "chuva", "sol"
            ],
            priority=SkillPriority.NORMAL,
            enabled_by_default=True
        )
    
    def initialize(self) -> bool:
        """Inicializa a skill."""
        # Validar dependências
        if not self.validate_dependencies():
            return False
        
        # API key pode ser opcional - skill pode funcionar com dados mock
        self.api_key = self.get_config('openweather_api_key')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            logger.warning(
                "Weather skill: API key não configurada. "
                "Usando modo de demonstração."
            )
            self.demo_mode = True
        else:
            self.demo_mode = False
            logger.info("Weather skill inicializada com OpenWeatherMap API")
        
        return True
    
    def can_handle(self, query: str, context: Dict[str, Any]) -> bool:
        """
        Verifica se a query é sobre clima.
        
        Args:
            query: Query do usuário
            context: Contexto da conversa
            
        Returns:
            bool: True se a query é sobre clima
        """
        query_lower = query.lower()
        
        # Palavras-chave que indicam consulta sobre clima
        weather_keywords = [
            'clima', 'tempo', 'temperatura', 'previsão',
            'weather', 'forecast', 'chuva', 'sol',
            'quente', 'frio', 'está chovendo', 'vai chover'
        ]
        
        return any(keyword in query_lower for keyword in weather_keywords)
    
    def execute(self, query: str, context: Dict[str, Any]) -> SkillResponse:
        """
        Executa a consulta de clima.
        
        Args:
            query: Query do usuário
            context: Contexto da conversa
            
        Returns:
            SkillResponse: Resposta com informações do clima
        """
        try:
            # Extrair cidade da query (se mencionada)
            city = self._extract_city(query)
            
            if not city:
                # Usar cidade padrão do contexto ou config
                city = context.get('user_city') or self.get_config('default_city', 'São Paulo')
            
            # Obter dados do clima
            if self.demo_mode:
                weather_data = self._get_demo_weather(city)
            else:
                weather_data = self._get_real_weather(city)
            
            if not weather_data:
                return SkillResponse.error_response(
                    f"Não foi possível obter informações do clima para {city}"
                )
            
            # Formatar resposta
            response_text = self._format_weather_response(city, weather_data)
            
            return SkillResponse.success_response(
                content=response_text,
                metadata={
                    'city': city,
                    'weather_data': weather_data,
                    'source': 'demo' if self.demo_mode else 'openweathermap'
                }
            )
        
        except Exception as e:
            logger.error(f"Erro ao executar Weather skill: {e}")
            return SkillResponse.error_response(str(e))
    
    def _extract_city(self, query: str) -> str:
        """
        Extrai nome da cidade da query.
        
        Args:
            query: Query do usuário
            
        Returns:
            str: Nome da cidade ou string vazia
        """
        # Padrões para identificar cidade
        patterns = [
            r'em\s+([A-Za-zÀ-ÿ\s]+)',  # "em São Paulo"
            r'de\s+([A-Za-zÀ-ÿ\s]+)',  # "de Lisboa"
            r'para\s+([A-Za-zÀ-ÿ\s]+)',  # "para Porto"
            r'in\s+([A-Za-zÀ-ÿ\s]+)',  # "in London"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                city = match.group(1).strip()
                # Remover palavras comuns que não são cidades
                stop_words = ['hoje', 'agora', 'amanhã', 'hoje', 'dia']
                if city.lower() not in stop_words:
                    return city
        
        return ""
    
    def _get_real_weather(self, city: str) -> Dict:
        """
        Obtém dados reais do clima via OpenWeatherMap.
        
        Args:
            city: Nome da cidade
            
        Returns:
            Dict: Dados do clima
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',  # Celsius
                'lang': 'pt_br'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'pressure': data['main']['pressure']
            }
        
        except Exception as e:
            logger.error(f"Erro ao obter clima real: {e}")
            return None
    
    def _get_demo_weather(self, city: str) -> Dict:
        """
        Retorna dados demo do clima.
        
        Args:
            city: Nome da cidade
            
        Returns:
            Dict: Dados demo
        """
        return {
            'temperature': 24.5,
            'feels_like': 26.0,
            'humidity': 65,
            'description': 'parcialmente nublado',
            'wind_speed': 12.5,
            'pressure': 1013
        }
    
    def _format_weather_response(self, city: str, data: Dict) -> str:
        """
        Formata resposta sobre o clima.
        
        Args:
            city: Nome da cidade
            data: Dados do clima
            
        Returns:
            str: Resposta formatada
        """
        response = f"🌡️ Clima em {city}:\n\n"
        response += f"• Temperatura: {data['temperature']:.1f}°C\n"
        response += f"• Sensação térmica: {data['feels_like']:.1f}°C\n"
        response += f"• Condição: {data['description'].capitalize()}\n"
        response += f"• Humidade: {data['humidity']}%\n"
        response += f"• Vento: {data['wind_speed']} km/h\n"
        response += f"• Pressão: {data['pressure']} hPa"
        
        return response


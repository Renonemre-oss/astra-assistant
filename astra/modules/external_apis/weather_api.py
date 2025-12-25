#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX - Weather API Integration
Integração com APIs de clima (OpenWeatherMap, AccuWeather)
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import json

from .base_api import BaseAPI

logger = logging.getLogger(__name__)

class WeatherAPI(BaseAPI):
    """Classe para integração com APIs de clima."""
    
    def __init__(self, provider: str = "openweathermap", api_key: str = "", language: str = "pt"):
        """
        Inicializa a API de clima.
        
        Args:
            provider: Provedor da API ('openweathermap' ou 'accuweather')
            api_key: Chave da API
            language: Idioma para as respostas
        """
        self.provider = provider.lower()
        self.language = language
        
        # Configurações específicas do provedor
        if self.provider == "openweathermap":
            base_url = "https://api.openweathermap.org/data/2.5"
            name = "OpenWeatherMap"
        elif self.provider == "accuweather":
            base_url = "http://dataservice.accuweather.com"
            name = "AccuWeather"
        else:
            raise ValueError(f"Provedor não suportado: {provider}")
        
        super().__init__(api_key, base_url, name)
        
        # Cache para reduzir requests
        self._cache = {}
        self._cache_duration = 300  # 5 minutos
        
        logger.info(f"WeatherAPI inicializada para {name}")
    
    def _test_api_connection(self) -> bool:
        """Testa a conexão com a API de clima."""
        try:
            if self.provider == "openweathermap":
                # Teste simples com Lisboa
                result = self.get("weather", params={
                    "q": "Lisboa,PT",
                    "appid": self.api_key,
                    "units": "metric"
                })
                return result is not None and "main" in result
            
            elif self.provider == "accuweather":
                # AccuWeather precisa de location key primeiro
                result = self.get("/locations/v1/cities/search", params={
                    "apikey": self.api_key,
                    "q": "Lisboa",
                    "language": self.language
                })
                return result is not None and len(result) > 0
            
            return False
        except Exception as e:
            logger.error(f"Erro ao testar conexão weather API: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Retorna as capacidades da API de clima."""
        return [
            "current_weather",
            "weather_forecast", 
            "weather_alerts",
            "location_search",
            "weather_history",
            "air_quality"
        ]
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se o cache ainda é válido."""
        if cache_key not in self._cache:
            return False
        
        cache_time = self._cache[cache_key].get("timestamp", 0)
        return (datetime.now().timestamp() - cache_time) < self._cache_duration
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Obtém dados do cache se válidos."""
        if self._is_cache_valid(cache_key):
            logger.debug(f"Usando cache para {cache_key}")
            return self._cache[cache_key]["data"]
        return None
    
    def _set_cache(self, cache_key: str, data: Dict):
        """Armazena dados no cache."""
        self._cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now().timestamp()
        }
    
    def get_current_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Obtém o clima atual para uma localização.
        
        Args:
            location: Nome da cidade ou coordenadas
            
        Returns:
            Dicionário com informações do clima atual
        """
        cache_key = f"current_{location}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            if self.provider == "openweathermap":
                result = self._get_openweather_current(location)
            elif self.provider == "accuweather":
                result = self._get_accuweather_current(location)
            else:
                return None
            
            if result:
                self._set_cache(cache_key, result)
                logger.info(f"Clima atual obtido para {location}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter clima atual: {e}")
            return None
    
    def _get_openweather_current(self, location: str) -> Optional[Dict[str, Any]]:
        """Obtém clima atual do OpenWeatherMap."""
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
            "lang": self.language
        }
        
        data = self.get("weather", params=params)
        if not data:
            return None
        
        return {
            "provider": "OpenWeatherMap",
            "location": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "description": data.get("weather", [{}])[0].get("description", "").title(),
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "wind_direction": data.get("wind", {}).get("deg"),
            "visibility": data.get("visibility"),
            "clouds": data.get("clouds", {}).get("all"),
            "sunrise": datetime.fromtimestamp(data.get("sys", {}).get("sunrise", 0)),
            "sunset": datetime.fromtimestamp(data.get("sys", {}).get("sunset", 0)),
            "timestamp": datetime.now()
        }
    
    def _get_accuweather_current(self, location: str) -> Optional[Dict[str, Any]]:
        """Obtém clima atual do AccuWeather."""
        # Primeiro, obter location key
        location_key = self._get_location_key(location)
        if not location_key:
            return None
        
        params = {
            "apikey": self.api_key,
            "language": self.language,
            "details": "true"
        }
        
        data = self.get(f"/currentconditions/v1/{location_key}", params=params)
        if not data or len(data) == 0:
            return None
        
        current = data[0]
        return {
            "provider": "AccuWeather",
            "location": location,
            "temperature": current.get("Temperature", {}).get("Metric", {}).get("Value"),
            "feels_like": current.get("RealFeelTemperature", {}).get("Metric", {}).get("Value"),
            "description": current.get("WeatherText", ""),
            "humidity": current.get("RelativeHumidity"),
            "pressure": current.get("Pressure", {}).get("Metric", {}).get("Value"),
            "wind_speed": current.get("Wind", {}).get("Speed", {}).get("Metric", {}).get("Value"),
            "wind_direction": current.get("Wind", {}).get("Direction", {}).get("Degrees"),
            "visibility": current.get("Visibility", {}).get("Metric", {}).get("Value"),
            "uv_index": current.get("UVIndex"),
            "timestamp": datetime.now()
        }
    
    def _get_location_key(self, location: str) -> Optional[str]:
        """Obtém location key do AccuWeather."""
        cache_key = f"location_key_{location}"
        cached_key = self._get_from_cache(cache_key)
        if cached_key:
            return cached_key
        
        params = {
            "apikey": self.api_key,
            "q": location,
            "language": self.language
        }
        
        data = self.get("/locations/v1/cities/search", params=params)
        if not data or len(data) == 0:
            return None
        
        location_key = data[0].get("Key")
        if location_key:
            self._set_cache(cache_key, location_key)
        
        return location_key
    
    def get_forecast(self, location: str, days: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Obtém previsão do tempo.
        
        Args:
            location: Nome da cidade
            days: Número de dias (1-5 para OpenWeather, 1-15 para AccuWeather)
            
        Returns:
            Lista com previsões diárias
        """
        cache_key = f"forecast_{location}_{days}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            if self.provider == "openweathermap":
                result = self._get_openweather_forecast(location, days)
            elif self.provider == "accuweather":
                result = self._get_accuweather_forecast(location, days)
            else:
                return None
            
            if result:
                self._set_cache(cache_key, result)
                logger.info(f"Previsão obtida para {location} ({days} dias)")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter previsão: {e}")
            return None
    
    def _get_openweather_forecast(self, location: str, days: int) -> Optional[List[Dict[str, Any]]]:
        """Obtém previsão do OpenWeatherMap."""
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric",
            "lang": self.language,
            "cnt": min(days * 8, 40)  # 8 previsões por dia (3h cada)
        }
        
        data = self.get("forecast", params=params)
        if not data:
            return None
        
        # Agrupar por dias
        daily_forecasts = {}
        
        for item in data.get("list", []):
            date = datetime.fromtimestamp(item.get("dt", 0)).date()
            
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    "date": date,
                    "temperatures": [],
                    "descriptions": [],
                    "humidity": [],
                    "wind_speed": []
                }
            
            daily_forecasts[date]["temperatures"].append(item.get("main", {}).get("temp"))
            daily_forecasts[date]["descriptions"].append(item.get("weather", [{}])[0].get("description", ""))
            daily_forecasts[date]["humidity"].append(item.get("main", {}).get("humidity"))
            daily_forecasts[date]["wind_speed"].append(item.get("wind", {}).get("speed"))
        
        # Processar dados agrupados
        forecast_list = []
        for date, day_data in sorted(daily_forecasts.items())[:days]:
            temps = day_data["temperatures"]
            forecast_list.append({
                "date": date,
                "temp_min": min(temps) if temps else None,
                "temp_max": max(temps) if temps else None,
                "description": max(set(day_data["descriptions"]), key=day_data["descriptions"].count),
                "humidity": sum(day_data["humidity"]) // len(day_data["humidity"]) if day_data["humidity"] else None,
                "wind_speed": sum(day_data["wind_speed"]) / len(day_data["wind_speed"]) if day_data["wind_speed"] else None
            })
        
        return forecast_list
    
    def _get_accuweather_forecast(self, location: str, days: int) -> Optional[List[Dict[str, Any]]]:
        """Obtém previsão do AccuWeather."""
        location_key = self._get_location_key(location)
        if not location_key:
            return None
        
        # AccuWeather tem diferentes endpoints para diferentes períodos
        if days <= 5:
            endpoint = f"/forecasts/v1/daily/5day/{location_key}"
        else:
            endpoint = f"/forecasts/v1/daily/15day/{location_key}"
        
        params = {
            "apikey": self.api_key,
            "language": self.language,
            "details": "true",
            "metric": "true"
        }
        
        data = self.get(endpoint, params=params)
        if not data:
            return None
        
        forecast_list = []
        for forecast in data.get("DailyForecasts", [])[:days]:
            date = datetime.fromisoformat(forecast.get("Date", "")).date()
            
            forecast_list.append({
                "date": date,
                "temp_min": forecast.get("Temperature", {}).get("Minimum", {}).get("Value"),
                "temp_max": forecast.get("Temperature", {}).get("Maximum", {}).get("Value"),
                "description": forecast.get("Day", {}).get("IconPhrase", ""),
                "precipitation_probability": forecast.get("Day", {}).get("PrecipitationProbability"),
                "wind_speed": forecast.get("Day", {}).get("Wind", {}).get("Speed", {}).get("Value")
            })
        
        return forecast_list
    
    def search_locations(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca localizações por nome.
        
        Args:
            query: Termo de busca
            
        Returns:
            Lista de localizações encontradas
        """
        try:
            if self.provider == "openweathermap":
                return self._search_openweather_locations(query)
            elif self.provider == "accuweather":
                return self._search_accuweather_locations(query)
            
        except Exception as e:
            logger.error(f"Erro ao buscar localizações: {e}")
            return []
    
    def _search_openweather_locations(self, query: str) -> List[Dict[str, Any]]:
        """Busca localizações no OpenWeatherMap."""
        params = {
            "q": query,
            "limit": 10,
            "appid": self.api_key
        }
        
        data = self.get("geo/1.0/direct", params=params)
        if not data:
            return []
        
        locations = []
        for location in data:
            locations.append({
                "name": location.get("name"),
                "country": location.get("country"),
                "state": location.get("state", ""),
                "lat": location.get("lat"),
                "lon": location.get("lon")
            })
        
        return locations
    
    def _search_accuweather_locations(self, query: str) -> List[Dict[str, Any]]:
        """Busca localizações no AccuWeather."""
        params = {
            "apikey": self.api_key,
            "q": query,
            "language": self.language
        }
        
        data = self.get("/locations/v1/cities/search", params=params)
        if not data:
            return []
        
        locations = []
        for location in data:
            locations.append({
                "name": location.get("LocalizedName"),
                "country": location.get("Country", {}).get("LocalizedName"),
                "state": location.get("AdministrativeArea", {}).get("LocalizedName", ""),
                "key": location.get("Key")
            })
        
        return locations
    
    def get_air_quality(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de qualidade do ar (apenas OpenWeatherMap).
        
        Args:
            location: Nome da cidade ou coordenadas lat,lon
            
        Returns:
            Dados de qualidade do ar ou None
        """
        if self.provider != "openweathermap":
            logger.warning("Qualidade do ar disponível apenas no OpenWeatherMap")
            return None
        
        try:
            # Se location não tem coordenadas, buscar primeiro
            if "," not in location:
                geo_data = self.get("geo/1.0/direct", params={
                    "q": location,
                    "limit": 1,
                    "appid": self.api_key
                })
                if not geo_data or len(geo_data) == 0:
                    return None
                lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
            else:
                lat, lon = location.split(",")
            
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key
            }
            
            data = self.get("air_pollution", params=params)
            if not data:
                return None
            
            aqi_levels = ["Bom", "Razoável", "Moderado", "Fraco", "Muito Fraco"]
            aqi = data.get("list", [{}])[0].get("main", {}).get("aqi", 1)
            
            return {
                "location": location,
                "aqi": aqi,
                "aqi_description": aqi_levels[aqi - 1] if 1 <= aqi <= 5 else "Desconhecido",
                "components": data.get("list", [{}])[0].get("components", {}),
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter qualidade do ar: {e}")
            return None
    
    def format_weather_response(self, weather_data: Dict[str, Any], include_forecast: bool = False) -> str:
        """
        Formata dados do clima para resposta em linguagem natural.
        
        Args:
            weather_data: Dados do clima
            include_forecast: Se deve incluir previsão
            
        Returns:
            Texto formatado com informações do clima
        """
        if not weather_data:
            return "❌ Não foi possível obter informações do clima."
        
        response = []
        
        # Clima atual
        location = weather_data.get("location", "Local desconhecido")
        temp = weather_data.get("temperature")
        feels_like = weather_data.get("feels_like")
        description = weather_data.get("description", "")
        
        response.append(f"🌤️ **Clima em {location}:**")
        
        if temp is not None:
            temp_text = f"🌡️ Temperatura: {temp:.1f}°C"
            if feels_like and abs(temp - feels_like) > 2:
                temp_text += f" (sensação: {feels_like:.1f}°C)"
            response.append(temp_text)
        
        if description:
            response.append(f"☁️ Condições: {description}")
        
        # Informações adicionais
        humidity = weather_data.get("humidity")
        if humidity:
            response.append(f"💧 Umidade: {humidity}%")
        
        wind_speed = weather_data.get("wind_speed")
        if wind_speed:
            response.append(f"🌬️ Vento: {wind_speed:.1f} km/h")
        
        pressure = weather_data.get("pressure")
        if pressure:
            response.append(f"📊 Pressão: {pressure} hPa")
        
        return "\n".join(response)
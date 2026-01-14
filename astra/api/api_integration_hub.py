#!/usr/bin/env python3
"""
API Integration Hub - Astra
Sistema unificado para integração de múltiplas APIs:
- Notícias (Newsdata.io)
- Clima (OpenWeatherMap)
- Ações/Stocks (Alpha Vantage / Yahoo Finance)
- Criptomoedas (CoinGecko)
- Scheduler automático
- Cache inteligente
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from dataclasses import dataclass, asdict
import schedule

# Importar módulos de APIs externas
try:
    from modules.external_apis.api_manager import APIManager
    EXTERNAL_APIS_AVAILABLE = True
except ImportError:
    EXTERNAL_APIS_AVAILABLE = False
    print("⚠️ Módulos de APIs externas não disponíveis")

@dataclass
class ApiResponse:
    """Classe para padronizar respostas das APIs"""
    source: str
    data: Any
    timestamp: datetime
    status: str
    error_message: Optional[str] = None

class ApiIntegrationHub:
    """Hub principal para integração de múltiplas APIs"""
    
    def __init__(self):
        self.api_keys = {
            'newsdata': 'pub_92678c58a16a41f3bccc1a9aeb11cae1',
            'openweather': None,  # Será configurado
            'alphavantage': None,  # Será configurado
            'coingecko': None     # API pública, não precisa de chave
        }
        
        self.cache = {}
        self.cache_duration = {
            'news': 300,        # 5 minutos
            'weather': 600,     # 10 minutos
            'stocks': 60,       # 1 minuto
            'crypto': 30        # 30 segundos
        }
        
        self.base_urls = {
            'newsdata': 'https://newsdata.io/api/1',
            'openweather': 'https://api.openweathermap.org/data/2.5',
            'alphavantage': 'https://www.alphavantage.co/query',
            'coingecko': 'https://api.coingecko.com/api/v3'
        }
        
        self.scheduler_active = False
        self.auto_update_data = {}
        
    def set_api_key(self, service: str, api_key: str):
        """Configurar chave de API para um serviço específico"""
        if service in self.api_keys:
            self.api_keys[service] = api_key
            print(f"✅ API key configurada para {service}")
        else:
            print(f"❌ Serviço {service} não reconhecido")
    
    def _is_cache_valid(self, cache_key: str, service_type: str) -> bool:
        """Verificar se o cache ainda é válido"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        duration = self.cache_duration.get(service_type, 300)
        
        return (datetime.now() - cached_time).seconds < duration
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Obter dados do cache se válido"""
        if self._is_cache_valid(cache_key, cache_key.split('_')[0]):
            return self.cache[cache_key]['data']
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Salvar dados no cache"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Fazer requisição HTTP com tratamento de erro"""
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            return None

class NewsAPI:
    """Classe para integração com Newsdata.io"""
    
    def __init__(self, hub: ApiIntegrationHub):
        self.hub = hub
        
    def get_latest_news(self, query: str = None, category: str = None, 
                       country: str = None, language: str = None, size: int = 10) -> ApiResponse:
        """Obter últimas notícias"""
        cache_key = f"news_{query or category or 'general'}_{size}"
        
        # Verificar cache
        cached_data = self.hub._get_from_cache(cache_key)
        if cached_data:
            return ApiResponse(
                source="newsdata_cached",
                data=cached_data,
                timestamp=datetime.now(),
                status="success"
            )
        
        # Fazer nova requisição
        url = f"{self.hub.base_urls['newsdata']}/latest"
        params = {
            'apikey': self.hub.api_keys['newsdata'],
            'size': size
        }
        
        if query:
            params['q'] = query
        if category:
            params['category'] = category
        if country:
            params['country'] = country
        if language:
            params['language'] = language
            
        data = self.hub._make_request(url, params)
        
        if data and data.get('status') == 'success':
            self.hub._save_to_cache(cache_key, data)
            return ApiResponse(
                source="newsdata",
                data=data,
                timestamp=datetime.now(),
                status="success"
            )
        else:
            return ApiResponse(
                source="newsdata",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message="Falha ao obter notícias"
            )

class WeatherAPI:
    """Classe para integração com OpenWeatherMap"""
    
    def __init__(self, hub: ApiIntegrationHub):
        self.hub = hub
        
    def get_current_weather(self, city: str = "São Paulo", country_code: str = "BR") -> ApiResponse:
        """Obter clima atual"""
        if not self.hub.api_keys['openweather']:
            return ApiResponse(
                source="openweather",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message="API key não configurada para OpenWeatherMap"
            )
        
        cache_key = f"weather_{city}_{country_code}"
        
        # Verificar cache
        cached_data = self.hub._get_from_cache(cache_key)
        if cached_data:
            return ApiResponse(
                source="openweather_cached",
                data=cached_data,
                timestamp=datetime.now(),
                status="success"
            )
        
        # Fazer nova requisição
        url = f"{self.hub.base_urls['openweather']}/weather"
        params = {
            'q': f"{city},{country_code}",
            'appid': self.hub.api_keys['openweather'],
            'units': 'metric',
            'lang': 'pt_br'
        }
        
        data = self.hub._make_request(url, params)
        
        if data:
            self.hub._save_to_cache(cache_key, data)
            return ApiResponse(
                source="openweather",
                data=data,
                timestamp=datetime.now(),
                status="success"
            )
        else:
            return ApiResponse(
                source="openweather",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message="Falha ao obter dados do clima"
            )
    
    def get_forecast(self, city: str = "São Paulo", country_code: str = "BR") -> ApiResponse:
        """Obter previsão do tempo (5 dias)"""
        if not self.hub.api_keys['openweather']:
            return ApiResponse(
                source="openweather",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message="API key não configurada"
            )
        
        cache_key = f"forecast_{city}_{country_code}"
        
        # Verificar cache
        cached_data = self.hub._get_from_cache(cache_key)
        if cached_data:
            return ApiResponse(
                source="openweather_forecast_cached",
                data=cached_data,
                timestamp=datetime.now(),
                status="success"
            )
        
        # Fazer nova requisição
        url = f"{self.hub.base_urls['openweather']}/forecast"
        params = {
            'q': f"{city},{country_code}",
            'appid': self.hub.api_keys['openweather'],
            'units': 'metric',
            'lang': 'pt_br',
            'cnt': 40  # 5 dias * 8 previsões por dia (3h cada)
        }
        
        data = self.hub._make_request(url, params)
        
        if data:
            self.hub._save_to_cache(cache_key, data)
            return ApiResponse(
                source="openweather_forecast",
                data=data,
                timestamp=datetime.now(),
                status="success"
            )
        else:
            return ApiResponse(
                source="openweather_forecast",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message="Falha ao obter previsão do tempo"
            )

class StocksAPI:
    """Classe para integração com APIs de ações/stocks"""
    
    def __init__(self, hub: ApiIntegrationHub):
        self.hub = hub
        # Usando Yahoo Finance API gratuita como alternativa
        self.yahoo_base = "https://query1.finance.yahoo.com/v8/finance/chart"
        
    def get_stock_quote(self, symbol: str) -> ApiResponse:
        """Obter cotação de uma ação específica"""
        cache_key = f"stock_{symbol.upper()}"
        
        # Verificar cache
        cached_data = self.hub._get_from_cache(cache_key)
        if cached_data:
            return ApiResponse(
                source="yahoo_finance_cached",
                data=cached_data,
                timestamp=datetime.now(),
                status="success"
            )
        
        # Fazer nova requisição usando Yahoo Finance
        url = f"{self.yahoo_base}/{symbol.upper()}"
        params = {
            'interval': '1d',
            'range': '1d'
        }
        
        data = self.hub._make_request(url, params)
        
        if data and data.get('chart', {}).get('result'):
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            
            # Processar dados para formato mais amigável
            processed_data = {
                'symbol': symbol.upper(),
                'name': meta.get('longName', symbol.upper()),
                'price': meta.get('regularMarketPrice', 0),
                'currency': meta.get('currency', 'USD'),
                'change': meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0),
                'change_percent': ((meta.get('regularMarketPrice', 0) - meta.get('previousClose', 0)) / meta.get('previousClose', 1)) * 100,
                'market_state': meta.get('marketState', 'UNKNOWN'),
                'timezone': meta.get('timezone', 'UTC'),
                'raw_data': data
            }
            
            self.hub._save_to_cache(cache_key, processed_data)
            return ApiResponse(
                source="yahoo_finance",
                data=processed_data,
                timestamp=datetime.now(),
                status="success"
            )
        else:
            return ApiResponse(
                source="yahoo_finance",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message=f"Falha ao obter dados da ação {symbol}"
            )
    
    def get_multiple_quotes(self, symbols: List[str]) -> List[ApiResponse]:
        """Obter cotações de múltiplas ações"""
        results = []
        for symbol in symbols:
            results.append(self.get_stock_quote(symbol))
            time.sleep(0.1)  # Evitar rate limiting
        return results
    
    def get_popular_stocks(self) -> ApiResponse:
        """Obter cotações de ações populares"""
        popular_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA']
        
        cache_key = "popular_stocks"
        cached_data = self.hub._get_from_cache(cache_key)
        if cached_data:
            return ApiResponse(
                source="popular_stocks_cached",
                data=cached_data,
                timestamp=datetime.now(),
                status="success"
            )
        
        quotes = []
        for symbol in popular_symbols:
            response = self.get_stock_quote(symbol)
            if response.status == "success":
                quotes.append(response.data)
        
        data = {
            'stocks': quotes,
            'count': len(quotes),
            'timestamp': datetime.now().isoformat()
        }
        
        if quotes:
            self.hub._save_to_cache(cache_key, data)
            return ApiResponse(
                source="popular_stocks",
                data=data,
                timestamp=datetime.now(),
                status="success"
            )
        else:
            return ApiResponse(
                source="popular_stocks",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message="Falha ao obter ações populares"
            )

class CryptoAPI:
    """Classe para integração com CoinGecko API (gratuita)"""
    
    def __init__(self, hub: ApiIntegrationHub):
        self.hub = hub
        
    def get_crypto_price(self, crypto_id: str, vs_currency: str = 'usd') -> ApiResponse:
        """Obter preço de uma criptomoeda específica"""
        cache_key = f"crypto_{crypto_id}_{vs_currency}"
        
        # Verificar cache
        cached_data = self.hub._get_from_cache(cache_key)
        if cached_data:
            return ApiResponse(
                source="coingecko_cached",
                data=cached_data,
                timestamp=datetime.now(),
                status="success"
            )
        
        # Fazer nova requisição
        url = f"{self.hub.base_urls['coingecko']}/simple/price"
        params = {
            'ids': crypto_id,
            'vs_currencies': vs_currency,
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        data = self.hub._make_request(url, params)
        
        if data and crypto_id in data:
            crypto_data = data[crypto_id]
            processed_data = {
                'id': crypto_id,
                'name': crypto_id.replace('-', ' ').title(),
                'price': crypto_data.get(vs_currency, 0),
                'currency': vs_currency.upper(),
                'change_24h': crypto_data.get(f'{vs_currency}_24h_change', 0),
                'volume_24h': crypto_data.get(f'{vs_currency}_24h_vol', 0),
                'market_cap': crypto_data.get(f'{vs_currency}_market_cap', 0),
                'raw_data': data
            }
            
            self.hub._save_to_cache(cache_key, processed_data)
            return ApiResponse(
                source="coingecko",
                data=processed_data,
                timestamp=datetime.now(),
                status="success"
            )
        else:
            return ApiResponse(
                source="coingecko",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message=f"Falha ao obter dados da criptomoeda {crypto_id}"
            )
    
    def get_popular_cryptos(self) -> ApiResponse:
        """Obter preços das principais criptomoedas"""
        cache_key = "popular_cryptos"
        cached_data = self.hub._get_from_cache(cache_key)
        if cached_data:
            return ApiResponse(
                source="popular_cryptos_cached",
                data=cached_data,
                timestamp=datetime.now(),
                status="success"
            )
        
        # Top 10 cryptos por market cap
        url = f"{self.hub.base_urls['coingecko']}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': 'false'
        }
        
        data = self.hub._make_request(url, params)
        
        if data:
            processed_cryptos = []
            for crypto in data:
                processed_cryptos.append({
                    'id': crypto.get('id', ''),
                    'symbol': crypto.get('symbol', '').upper(),
                    'name': crypto.get('name', ''),
                    'price': crypto.get('current_price', 0),
                    'market_cap_rank': crypto.get('market_cap_rank', 0),
                    'market_cap': crypto.get('market_cap', 0),
                    'change_24h': crypto.get('price_change_percentage_24h', 0),
                    'volume_24h': crypto.get('total_volume', 0),
                    'image': crypto.get('image', ''),
                })
            
            result_data = {
                'cryptos': processed_cryptos,
                'count': len(processed_cryptos),
                'timestamp': datetime.now().isoformat()
            }
            
            self.hub._save_to_cache(cache_key, result_data)
            return ApiResponse(
                source="popular_cryptos",
                data=result_data,
                timestamp=datetime.now(),
                status="success"
            )
        else:
            return ApiResponse(
                source="popular_cryptos",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message="Falha ao obter criptomoedas populares"
            )
    
    def get_trending_cryptos(self) -> ApiResponse:
        """Obter criptomoedas em trending"""
        cache_key = "trending_cryptos"
        cached_data = self.hub._get_from_cache(cache_key)
        if cached_data:
            return ApiResponse(
                source="trending_cryptos_cached",
                data=cached_data,
                timestamp=datetime.now(),
                status="success"
            )
        
        url = f"{self.hub.base_urls['coingecko']}/search/trending"
        data = self.hub._make_request(url)
        
        if data and 'coins' in data:
            trending_coins = []
            for item in data['coins']:
                coin = item['item']
                trending_coins.append({
                    'id': coin.get('id', ''),
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name', ''),
                    'rank': coin.get('market_cap_rank', 0),
                    'image': coin.get('large', ''),
                })
            
            result_data = {
                'trending_coins': trending_coins,
                'count': len(trending_coins),
                'timestamp': datetime.now().isoformat()
            }
            
            self.hub._save_to_cache(cache_key, result_data)
            return ApiResponse(
                source="trending_cryptos",
                data=result_data,
                timestamp=datetime.now(),
                status="success"
            )
        else:
            return ApiResponse(
                source="trending_cryptos",
                data=None,
                timestamp=datetime.now(),
                status="error",
                error_message="Falha ao obter criptomoedas em trending"
            )

class SchedulerManager:
    """Gerenciador do scheduler automático"""
    
    def __init__(self, hub: ApiIntegrationHub):
        self.hub = hub
        self.scheduler_thread = None
        self.is_running = False
        
    def start_scheduler(self):
        """Iniciar o scheduler automático"""
        if self.is_running:
            print("⚠️ Scheduler já está executando")
            return
        
        # Configurar tarefas agendadas
        schedule.clear()
        
        # Atualizar notícias a cada 5 minutos
        schedule.every(5).minutes.do(self._update_news)
        
        # Atualizar crypto a cada 30 segundos
        schedule.every(30).seconds.do(self._update_crypto)
        
        # Atualizar stocks a cada 1 minuto
        schedule.every(1).minutes.do(self._update_stocks)
        
        # Atualizar clima a cada 10 minutos
        schedule.every(10).minutes.do(self._update_weather)
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("✅ Scheduler automático iniciado!")
        print("📊 Atualizações: Notícias (5min), Crypto (30s), Stocks (1min), Clima (10min)")
    
    def stop_scheduler(self):
        """Parar o scheduler"""
        self.is_running = False
        schedule.clear()
        print("⏹️ Scheduler automático parado")
    
    def _run_scheduler(self):
        """Executar o loop do scheduler"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
    
    def _update_news(self):
        """Atualizar notícias automaticamente"""
        try:
            news_api = NewsAPI(self.hub)
            response = news_api.get_latest_news(query="tecnologia", size=5)
            if response.status == "success":
                self.hub.auto_update_data['news'] = response.data
                print(f"📰 Notícias atualizadas: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Erro ao atualizar notícias: {e}")
    
    def _update_crypto(self):
        """Atualizar criptomoedas automaticamente"""
        try:
            crypto_api = CryptoAPI(self.hub)
            response = crypto_api.get_popular_cryptos()
            if response.status == "success":
                self.hub.auto_update_data['crypto'] = response.data
                print(f"💰 Crypto atualizado: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Erro ao atualizar crypto: {e}")
    
    def _update_stocks(self):
        """Atualizar ações automaticamente"""
        try:
            stocks_api = StocksAPI(self.hub)
            response = stocks_api.get_popular_stocks()
            if response.status == "success":
                self.hub.auto_update_data['stocks'] = response.data
                print(f"📈 Stocks atualizados: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Erro ao atualizar stocks: {e}")
    
    def _update_weather(self):
        """Atualizar clima automaticamente"""
        try:
            if self.hub.api_keys['openweather']:
                weather_api = WeatherAPI(self.hub)
                response = weather_api.get_current_weather()
                if response.status == "success":
                    self.hub.auto_update_data['weather'] = response.data
                    print(f"🌤️ Clima atualizado: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Erro ao atualizar clima: {e}")

class UnifiedDashboard:
    """Dashboard unificado para todos os dados"""
    
    def __init__(self, hub: ApiIntegrationHub):
        self.hub = hub
        self.news_api = NewsAPI(hub)
        self.stocks_api = StocksAPI(hub)
        self.crypto_api = CryptoAPI(hub)
        self.weather_api = WeatherAPI(hub)
        
        # Inicializar APIs externas se disponíveis
        if EXTERNAL_APIS_AVAILABLE:
            self.external_apis = APIManager()
        else:
            self.external_apis = None
    
    def display_dashboard(self):
        """Exibir dashboard completo"""
        print("\n" + "="*80)
        print("🚀 Astra API INTEGRATION HUB - DASHBOARD")
        print("="*80)
        
        # Seção de Notícias
        print("\n📰 ÚLTIMAS NOTÍCIAS")
        print("-"*50)
        self._display_news_section()
        
        # Seção de Ações
        print("\n📈 AÇÕES POPULARES")
        print("-"*50)
        self._display_stocks_section()
        
        # Seção de Criptomoedas
        print("\n💰 CRIPTOMOEDAS")
        print("-"*50)
        self._display_crypto_section()
        
        # Seção de Clima (se configurado)
        if self.hub.api_keys['openweather']:
            print("\n🌤️ CLIMA")
            print("-"*50)
            self._display_weather_section()
        
        # Seção de APIs Externas (se disponível)
        if self.external_apis:
            print("\n🔗 INTEGRAÇÕES EXTERNAS")
            print("-"*50)
            self._display_external_apis_section()
        
        print("\n" + "="*80)
        print(f"⏰ Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("="*80)
    
    def _display_news_section(self):
        """Exibir seção de notícias"""
        try:
            response = self.news_api.get_latest_news(query="tecnologia", size=3)
            if response.status == "success" and response.data:
                articles = response.data.get('results', [])
                for i, article in enumerate(articles[:3], 1):
                    title = article.get('title', 'Sem título')
                    source = article.get('source_name', 'Fonte desconhecida')
                    if len(title) > 65:
                        title = title[:65] + "..."
                    print(f"  {i}. {title}")
                    print(f"     📰 {source}")
            else:
                print("  ❌ Não foi possível carregar notícias")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    def _display_stocks_section(self):
        """Exibir seção de ações"""
        try:
            response = self.stocks_api.get_popular_stocks()
            if response.status == "success" and response.data:
                stocks = response.data.get('stocks', [])[:5]
                for stock in stocks:
                    symbol = stock.get('symbol', 'N/A')
                    price = stock.get('price', 0)
                    change_pct = stock.get('change_percent', 0)
                    
                    change_indicator = "🔴" if change_pct < 0 else "🟢"
                    print(f"  {symbol}: ${price:.2f} {change_indicator} {change_pct:+.2f}%")
            else:
                print("  ❌ Não foi possível carregar ações")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    def _display_crypto_section(self):
        """Exibir seção de criptomoedas"""
        try:
            response = self.crypto_api.get_popular_cryptos()
            if response.status == "success" and response.data:
                cryptos = response.data.get('cryptos', [])[:5]
                for crypto in cryptos:
                    symbol = crypto.get('symbol', 'N/A')
                    price = crypto.get('price', 0)
                    change_24h = crypto.get('change_24h', 0)
                    
                    change_indicator = "🔴" if change_24h < 0 else "🟢"
                    print(f"  {symbol}: ${price:,.2f} {change_indicator} {change_24h:+.2f}%")
            else:
                print("  ❌ Não foi possível carregar criptomoedas")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    def _display_weather_section(self):
        """Exibir seção do clima"""
        try:
            response = self.weather_api.get_current_weather()
            if response.status == "success" and response.data:
                weather = response.data
                city = weather.get('name', 'N/A')
                temp = weather.get('main', {}).get('temp', 0)
                desc = weather.get('weather', [{}])[0].get('description', 'N/A')
                humidity = weather.get('main', {}).get('humidity', 0)
                
                print(f"  🌍 {city}: {temp:.1f}°C")
                print(f"  🌤️ {desc.title()}")
                print(f"  💧 Umidade: {humidity}%")
            else:
                print("  ❌ Configure sua API key do OpenWeatherMap")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    def _display_external_apis_section(self):
        """Объявить seção das APIs externas"""
        try:
            status_items = []
            
            # Verificar RSS/News
            try:
                if os.getenv("NEWS_API_KEY"):
                    status_items.append("📰 NewsAPI: ✓ Configurado")
                else:
                    status_items.append("📰 RSS: ✓ Disponível")
            except:
                status_items.append("📰 News: ❌ Indisponível")
            
            # Verificar Calendar
            if os.getenv("GOOGLE_CALENDAR_TOKEN") or os.getenv("MS_GRAPH_TOKEN"):
                cal_providers = []
                if os.getenv("GOOGLE_CALENDAR_TOKEN"):
                    cal_providers.append("Google")
                if os.getenv("MS_GRAPH_TOKEN"):
                    cal_providers.append("Outlook")
                status_items.append(f"📅 Calendário: ✓ {', '.join(cal_providers)}")
            else:
                status_items.append("📅 Calendário: ❌ Não configurado")
            
            # Verificar Email
            email_providers = []
            if os.getenv("GMAIL_TOKEN"):
                email_providers.append("Gmail")
            if os.getenv("MS_GRAPH_TOKEN"):
                email_providers.append("Outlook")
            if email_providers:
                status_items.append(f"📧 Email: ✓ {', '.join(email_providers)}")
            else:
                status_items.append("📧 Email: ❌ Não configurado")
            
            # Verificar Social Media
            social_providers = []
            if os.getenv("TWITTER_BEARER_TOKEN"):
                social_providers.append("Twitter")
            if os.getenv("LINKEDIN_ACCESS_TOKEN"):
                social_providers.append("LinkedIn")
            if social_providers:
                status_items.append(f"📱 Social: ✓ {', '.join(social_providers)}")
            else:
                status_items.append("📱 Social: ❌ Não configurado")
            
            # Exibir status
            for item in status_items[:4]:  # Mostrar apenas 4 primeiros
                print(f"  {item}")
                
        except Exception as e:
            print(f"  ❌ Erro ao verificar APIs externas: {e}")

# Inicialização
if __name__ == "__main__":
    print("🚀 Inicializando API Integration Hub...")
    
    # Criar hub principal
    hub = ApiIntegrationHub()
    
    # Criar dashboard
    dashboard = UnifiedDashboard(hub)
    
    # Configurar APIs (descomente e adicione suas chaves)
    # hub.set_api_key('openweather', 'YOUR_OPENWEATHER_API_KEY')
    
    try:
        # Exibir dashboard inicial
        dashboard.display_dashboard()
        
        # Opção de iniciar scheduler
        print("\n🤖 Opções disponíveis:")
        print("1. Executar dashboard uma vez")
        print("2. Iniciar scheduler automático (Ctrl+C para parar)")
        
        choice = input("\nEscolha uma opção (1 ou 2): ").strip()
        
        if choice == "2":
            scheduler = SchedulerManager(hub)
            scheduler.start_scheduler()
            
            print("\n⏰ Scheduler ativo! Pressione Ctrl+C para parar...")
            try:
                while True:
                    time.sleep(10)
                    # Mostrar status do cache
                    print(f"\n📊 Status do Cache ({len(hub.cache)} itens):")
                    for key in list(hub.cache.keys())[:5]:  # Mostrar apenas 5
                        age = (datetime.now() - hub.cache[key]['timestamp']).seconds
                        print(f"  {key}: {age}s atrás")
                    
            except KeyboardInterrupt:
                scheduler.stop_scheduler()
                print("\n👋 Scheduler parado. Até logo!")
        
        else:
            print("\n✅ Dashboard executado com sucesso!")
            print("💡 Dica: Execute novamente com opção 2 para modo automático")
            
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")


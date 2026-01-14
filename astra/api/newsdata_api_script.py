#!/usr/bin/env python3
"""
Newsdata.io API Script
A Python script to fetch latest news using the Newsdata.io API.
"""

import requests
import json
from datetime import datetime

class NewsdataAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsdata.io/api/1"
    
    def get_latest_news(self, query=None, language=None, country=None, category=None, size=10):
        """
        Fetch latest news from Newsdata.io API
        
        Args:
            query (str): Search query
            language (str): Language code (e.g., 'en', 'es')
            country (str): Country code (e.g., 'us', 'gb')
            category (str): Category (e.g., 'technology', 'business', 'sports')
            size (int): Number of articles to fetch (max 50 for free tier)
        """
        url = f"{self.base_url}/latest"
        
        params = {
            'apikey': self.api_key,
            'size': size
        }
        
        if query:
            params['q'] = query
        if language:
            params['language'] = language
        if country:
            params['country'] = country
        if category:
            params['category'] = category
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success':
                return data
            else:
                print(f"API Error: {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
    
    def display_articles(self, data):
        """Display articles in a readable format"""
        if not data or 'results' not in data:
            print("No articles to display")
            return
        
        articles = data['results']
        total_results = data.get('totalResults', len(articles))
        
        print(f"Found {total_results} articles. Showing {len(articles)} articles:")
        print("=" * 80)
        
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.get('title', 'No title')}")
            print(f"   Source: {article.get('source_name', 'Unknown source')}")
            
            # Format date
            pub_date = article.get('pubDate', '')
            if pub_date:
                try:
                    dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                    print(f"   Date: {formatted_date}")
                except:
                    print(f"   Date: {pub_date}")
            
            # Display description if available
            description = article.get('description', '')
            if description:
                # Truncate long descriptions
                if len(description) > 200:
                    description = description[:200] + "..."
                print(f"   Description: {description}")
            
            # Display link
            link = article.get('link', '')
            if link:
                print(f"   URL: {link}")
            
            # Display categories if available
            categories = article.get('category', [])
            if categories:
                print(f"   Categories: {', '.join(categories)}")
            
            print("-" * 80)

def search_multiple_topics(news_api):
    """Search for news across multiple topics and categories"""
    topics = {
        "Tecnologia": ["tech", "inteligência artificial", "AI", "smartphone", "software"],
        "Negócios": ["business", "economia", "mercado financeiro", "investimentos", "startups"],
        "Esportes": ["futebol", "basketball", "olimpiadas", "tennis", "formula 1"],
        "Saúde": ["medicina", "covid", "vacina", "saúde mental", "pesquisa médica"],
        "Ciência": ["space", "nasa", "pesquisa científica", "clima", "energia renovável"],
        "Entretenimento": ["cinema", "música", "Netflix", "streaming", "celebridades"],
        "Política": ["eleições", "governo", "políticas públicas", "democracia"],
        "Educação": ["universidade", "ensino", "educação online", "pesquisa acadêmica"]
    }
    
    print("🔍 Buscando notícias em múltiplos tópicos...\n")
    
    for category, keywords in topics.items():
        print(f"📂 {category.upper()}")
        print("=" * 50)
        
        # Try each keyword until we find articles
        found_articles = False
        for keyword in keywords:
            data = news_api.get_latest_news(query=keyword, size=3)
            if data and data.get('results'):
                print(f"🔍 Palavra-chave: '{keyword}' ({data.get('totalResults', 0)} resultados disponíveis)")
                
                articles = data['results'][:3]  # Show only 3 per keyword
                for i, article in enumerate(articles, 1):
                    title = article.get('title', 'Sem título')[:80] + "..." if len(article.get('title', '')) > 80 else article.get('title', 'Sem título')
                    source = article.get('source_name', 'Fonte desconhecida')
                    
                    pub_date = article.get('pubDate', '')
                    if pub_date:
                        try:
                            dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                            formatted_date = dt.strftime('%d/%m %H:%M')
                        except:
                            formatted_date = pub_date[:10]
                    else:
                        formatted_date = 'Data não disponível'
                    
                    print(f"  {i}. {title}")
                    print(f"     📰 {source} | 📅 {formatted_date}")
                    if article.get('link'):
                        print(f"     🔗 {article['link']}")
                    print()
                
                found_articles = True
                break  # Found articles for this category, move to next
        
        if not found_articles:
            print("   ❌ Nenhum artigo encontrado para esta categoria")
        
        print("-" * 80)
        print()

def search_by_categories(news_api):
    """Search news by predefined categories"""
    categories = {
        "technology": "🔬 Tecnologia",
        "business": "💼 Negócios", 
        "sports": "⚽ Esportes",
        "health": "🏥 Saúde",
        "entertainment": "🎬 Entretenimento",
        "science": "🧬 Ciência",
        "politics": "🏛️ Política"
    }
    
    print("📊 NOTÍCIAS POR CATEGORIA\n")
    
    for category_key, category_name in categories.items():
        print(f"{category_name}")
        print("=" * 50)
        
        data = news_api.get_latest_news(category=category_key, size=3)
        
        if data and data.get('results'):
            articles = data['results']
            print(f"📈 {data.get('totalResults', 0)} artigos disponíveis | Mostrando {len(articles)}")
            
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'Sem título')
                if len(title) > 70:
                    title = title[:70] + "..."
                
                source = article.get('source_name', 'Fonte desconhecida')
                print(f"  {i}. {title}")
                print(f"     📰 {source}")
                
                if article.get('description'):
                    desc = article['description'][:100] + "..." if len(article['description']) > 100 else article['description']
                    print(f"     💬 {desc}")
                print()
        else:
            print("   ❌ Nenhum artigo encontrado")
        
        print("-" * 80)
        print()

def main():
    # Your Newsdata.io API key
    api_key = "pub_92678c58a16a41f3bccc1a9aeb11cae1"
    
    # Initialize the API client
    news_api = NewsdataAPI(api_key)
    
    print("🚀 Newsdata.io API Client inicializado!")
    print("📰 Sistema de Notícias Multi-Tópicos\n")
    
    # Show menu
    print("Escolha uma opção:")
    print("1. Buscar por múltiplos tópicos (palavras-chave)")
    print("2. Buscar por categorias predefinidas")
    print("3. Buscar tópico específico")
    
    try:
        choice = input("\nDigite sua escolha (1, 2, ou 3): ").strip()
        
        if choice == "1":
            search_multiple_topics(news_api)
        elif choice == "2":
            search_by_categories(news_api)
        elif choice == "3":
            query = input("Digite o tópico que deseja pesquisar: ").strip()
            if query:
                print(f"\n🔍 Buscando notícias sobre '{query}'...\n")
                data = news_api.get_latest_news(query=query, size=10)
                if data:
                    news_api.display_articles(data)
                else:
                    print("❌ Falha ao buscar dados de notícias")
            else:
                print("❌ Por favor, digite um tópico válido")
        else:
            print("❌ Opção inválida. Executando busca padrão por tecnologia...")
            data = news_api.get_latest_news(query="tech", size=10)
            if data:
                news_api.display_articles(data)
    
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n" + "="*80)
    print("💡 DICAS PARA PERSONALIZAR:")
    print("- Modifique as listas de palavras-chave em 'topics'")
    print("- Adicione novas categorias")
    print("- Ajuste o número de artigos por tópico")
    print("- Filtre por país usando country='us', 'br', etc.")
    print("- Filtre por idioma usando language='en', 'pt', etc.")

if __name__ == "__main__":
    main()
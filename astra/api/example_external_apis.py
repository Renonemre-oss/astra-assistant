#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemplo de uso das novas integrações com APIs externas no Astra.
Este arquivo demonstra como usar as funcionalidades de:
- Notícias (RSS/NewsAPI)
- Calendário (Google/Outlook) 
- Email (Gmail/Outlook)
- Redes Sociais (Twitter/LinkedIn)
"""

import os
from modules.external_apis.api_manager import APIManager

def exemplo_news():
    """Exemplo de uso da NewsAPI"""
    print("📰 TESTE: API de Notícias")
    print("-" * 40)
    
    manager = APIManager()
    
    # Testar RSS feed
    print("🔗 Testando RSS Feed:")
    result = manager.news.from_rss("https://rss.cnn.com/rss/edition.rss", limit=3)
    if result.get('data') and result['data'].get('results'):
        for item in result['data']['results'][:3]:
            print(f"  - {item.get('title', 'Sem título')}")
    else:
        print(f"  ❌ Erro: {result.get('error', 'Desconhecido')}")
    
    # Testar NewsData (se configurado)
    if os.getenv("NEWS_API_KEY"):
        print("\n📡 Testando NewsData API:")
        result = manager.news.latest(query="tecnologia", size=3)
        if result.get('data') and result['data'].get('results'):
            for item in result['data']['results'][:3]:
                print(f"  - {item.get('title', 'Sem título')}")
        else:
            print(f"  ❌ Erro: {result.get('error', 'Falha na API')}")
    else:
        print("\n⚠️ NEWS_API_KEY não configurada")

def exemplo_calendar():
    """Exemplo de uso da CalendarAPI"""
    print("\n📅 TESTE: API de Calendário")
    print("-" * 40)
    
    manager = APIManager()
    
    # Google Calendar
    if os.getenv("GOOGLE_CALENDAR_TOKEN"):
        print("🟢 Testando Google Calendar:")
        result = manager.calendar.google_list_events(max_results=3)
        if result.get('data') and result['data'].get('items'):
            for event in result['data']['items'][:3]:
                print(f"  - {event.get('summary', 'Evento sem título')}")
        else:
            print(f"  ❌ Erro: {result.get('error', 'Falha na API')}")
    else:
        print("⚠️ GOOGLE_CALENDAR_TOKEN não configurada")
    
    # Microsoft Outlook
    if os.getenv("MS_GRAPH_TOKEN"):
        print("\n🔵 Testando Microsoft Outlook:")
        result = manager.calendar.outlook_list_events(max_results=3)
        if result.get('data') and result['data'].get('value'):
            for event in result['data']['value'][:3]:
                print(f"  - {event.get('subject', 'Evento sem título')}")
        else:
            print(f"  ❌ Erro: {result.get('error', 'Falha na API')}")
    else:
        print("⚠️ MS_GRAPH_TOKEN não configurada")

def exemplo_email():
    """Exemplo de uso da EmailAPI"""
    print("\n📧 TESTE: API de Email")
    print("-" * 40)
    
    manager = APIManager()
    
    # Gmail
    if os.getenv("GMAIL_TOKEN"):
        print("🟢 Testando Gmail:")
        result = manager.email.gmail_list_messages(max_results=3)
        if result.get('data') and result['data'].get('messages'):
            print(f"  ✓ Encontradas {len(result['data']['messages'])} mensagens")
        else:
            print(f"  ❌ Erro: {result.get('error', 'Falha na API')}")
    else:
        print("⚠️ GMAIL_TOKEN não configurada")
    
    # Outlook
    if os.getenv("MS_GRAPH_TOKEN"):
        print("\n🔵 Testando Outlook:")
        result = manager.email.outlook_list_messages(max_results=3)
        if result.get('data') and result['data'].get('value'):
            print(f"  ✓ Encontradas {len(result['data']['value'])} mensagens")
            for msg in result['data']['value'][:3]:
                print(f"  - {msg.get('subject', 'Sem assunto')}")
        else:
            print(f"  ❌ Erro: {result.get('error', 'Falha na API')}")
    else:
        print("⚠️ MS_GRAPH_TOKEN não configurada")

def exemplo_social():
    """Exemplo de uso da SocialMediaAPI"""
    print("\n📱 TESTE: API de Redes Sociais")
    print("-" * 40)
    
    manager = APIManager()
    
    # Twitter
    if os.getenv("TWITTER_BEARER_TOKEN"):
        print("🐦 Testando Twitter:")
        if os.getenv("TWITTER_USER_ID"):
            user_id = os.getenv("TWITTER_USER_ID")
            result = manager.social.twitter_user_timeline(user_id, max_results=3)
            if result.get('data') and result['data'].get('data'):
                print(f"  ✓ Encontrados {len(result['data']['data'])} tweets")
            else:
                print(f"  ❌ Erro: {result.get('error', 'Falha na API')}")
        else:
            print("  ⚠️ TWITTER_USER_ID não configurado")
    else:
        print("⚠️ TWITTER_BEARER_TOKEN não configurada")
    
    # LinkedIn
    if os.getenv("LINKEDIN_ACCESS_TOKEN") and os.getenv("LINKEDIN_URN"):
        print("\n🔗 LinkedIn configurado ✓")
    else:
        print("\n⚠️ LinkedIn não configurado (LINKEDIN_ACCESS_TOKEN/LINKEDIN_URN)")

def main():
    """Função principal para testar todas as APIs"""
    print("🚀 Astra - Teste de APIs Externas")
    print("=" * 50)
    print("Este teste verifica a configuração e conectividade")
    print("das APIs externas integradas ao Astra.\n")
    
    try:
        exemplo_news()
        exemplo_calendar()
        exemplo_email()
        exemplo_social()
        
        print("\n" + "=" * 50)
        print("✅ Teste concluído!")
        print("\n💡 Para configurar as APIs, defina as variáveis de ambiente:")
        print("   - NEWS_API_KEY (opcional)")
        print("   - GOOGLE_CALENDAR_TOKEN")
        print("   - MS_GRAPH_TOKEN")
        print("   - GMAIL_TOKEN")
        print("   - TWITTER_BEARER_TOKEN")
        print("   - TWITTER_USER_ID")
        print("   - LINKEDIN_ACCESS_TOKEN")
        print("   - LINKEDIN_URN")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

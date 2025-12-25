#!/usr/bin/env python3
"""
EventRegistry Script
A Python script to work with EventRegistry API for news and event data retrieval.
"""

from eventregistry import EventRegistry
import os
import json

def main():
    # Initialize EventRegistry
    # Replace "YOUR_API_KEY" with your actual API key
    # You can also set it as an environment variable: os.getenv('EVENT_REGISTRY_API_KEY')
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    
    # Alternative: Use environment variable for security
    # api_key = os.getenv('EVENT_REGISTRY_API_KEY')
    # if not api_key:
    #     print("Please set EVENT_REGISTRY_API_KEY environment variable or update the script with your API key")
    #     return
    
    try:
        # Initialize EventRegistry instance
        er = EventRegistry(apiKey=api_key, allowUseOfArchive=False)
        print("EventRegistry initialized successfully!")
        
        # Example: Get recent articles about a topic
        # Uncomment and modify as needed
        """
        from eventregistry import QueryArticlesIter
        
        q = QueryArticlesIter(
            keywords="artificial intelligence",
            lang="eng"
        )
        
        # Get first 10 articles
        articles = []
        for article in q.execQuery(er, sortBy="date", maxItems=10):
            articles.append({
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'date': article.get('date', ''),
                'source': article.get('source', {}).get('title', '')
            })
        
        print(f"Found {len(articles)} articles:")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Date: {article['date']}")
            print(f"   URL: {article['url']}")
            print()
        """
        
        # Add your EventRegistry code here
        print("Ready to use EventRegistry!")
        print("Add your specific queries and operations below.")
        
    except Exception as e:
        print(f"Error initializing EventRegistry: {e}")
        print("Make sure you have a valid API key and internet connection.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - API Client Example
Basic example of using the REST API.
"""

import requests
import json
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8001"


class AlexAPIClient:
    """Simple API client for ALEX/JARVIS."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def send_message(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Send a message to the assistant.
        
        Args:
            message: Message text
            user_id: User identifier
            
        Returns:
            API response
        """
        response = self.session.post(
            f"{self.base_url}/api/v1/conversation/message",
            json={
                "message": message,
                "user_id": user_id,
                "context": {}
            }
        )
        response.raise_for_status()
        return response.json()
        
    def get_history(self, user_id: str = "default", limit: int = 10) -> Dict[str, Any]:
        """Get conversation history."""
        response = self.session.get(
            f"{self.base_url}/api/v1/conversation/history",
            params={"user_id": user_id, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
        
    def set_personality(self, mode: str) -> Dict[str, Any]:
        """Set personality mode."""
        response = self.session.post(
            f"{self.base_url}/api/v1/personality/set",
            json={"mode": mode}
        )
        response.raise_for_status()
        return response.json()
        
    def store_memory(self, content: str, tags: list = None) -> Dict[str, Any]:
        """Store a memory."""
        response = self.session.post(
            f"{self.base_url}/api/v1/memory/store",
            json={
                "content": content,
                "memory_type": "semantic",
                "importance": "medium",
                "tags": tags or []
            }
        )
        response.raise_for_status()
        return response.json()
        
    def recall_memories(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Recall memories."""
        response = self.session.get(
            f"{self.base_url}/api/v1/memory/recall",
            params={"query": query, "max_results": max_results}
        )
        response.raise_for_status()
        return response.json()
        
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = self.session.get(f"{self.base_url}/api/v1/system/health")
        response.raise_for_status()
        return response.json()


def main():
    """Example usage."""
    print("🤖 ALEX/JARVIS API Client Example\n")
    
    # Create client
    client = AlexAPIClient()
    
    try:
        # 1. Health check
        print("1. Checking API health...")
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Version: {health['version']}\n")
        
        # 2. Send a message
        print("2. Sending message...")
        response = client.send_message("Hello, how are you?")
        print(f"   Response: {response['response']}\n")
        
        # 3. Set personality
        print("3. Setting personality to 'friendly'...")
        result = client.set_personality("friendly")
        print(f"   Personality set: {result['personality']}\n")
        
        # 4. Store a memory
        print("4. Storing a memory...")
        memory = client.store_memory(
            "User likes Python programming",
            tags=["preference", "programming"]
        )
        print(f"   Memory stored: {memory['memory_id']}\n")
        
        # 5. Recall memories
        print("5. Recalling memories about 'Python'...")
        memories = client.recall_memories("Python", max_results=5)
        print(f"   Found {memories['total']} memories\n")
        
        # 6. Get conversation history
        print("6. Getting conversation history...")
        history = client.get_history(limit=5)
        print(f"   Total messages: {history['total']}\n")
        
        print("✅ All API calls successful!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("   Make sure the server is running: python jarvis/api_server/main.py")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NewsAPI - Integração com NewsData e RSS feeds.
- Provider "newsdata": https://newsdata.io
- Provider "rss": qualquer URL RSS/Atom

Requerimentos:
- Para newsdata: defina NEWS_API_KEY (opcional; alguns planos gratuitos usam chave pública)
"""

from __future__ import annotations

import os
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_api import BaseAPI

logger = logging.getLogger(__name__)


class NewsAPI(BaseAPI):
    def __init__(self, provider: str = "newsdata", api_key: Optional[str] = None):
        provider = provider.lower()
        if provider == "newsdata":
            base_url = "https://newsdata.io/api/1/"
            name = "Newsdata"
            api_key = api_key or os.getenv("NEWS_API_KEY")
        elif provider == "newsapi":
            base_url = "https://newsapi.org/v2/"
            name = "NewsAPI"
            api_key = api_key or os.getenv("NEWS_API_KEY")
        elif provider == "rss":
            base_url = ""  # RSS usa URL completa
            name = "RSS"
        else:
            raise ValueError(f"Provider não suportado: {provider}")

        super().__init__(api_key=api_key, base_url=base_url, name=name)
        self.provider = provider

    def latest(self, query: Optional[str] = None, category: Optional[str] = None, language: Optional[str] = None, size: int = 10) -> Dict[str, Any]:
        if self.provider == "newsdata":
            params = {"apikey": self.api_key, "size": size}
            if query:
                params["q"] = query
            if category:
                params["category"] = category
            if language:
                params["language"] = language
            data = self.get("latest", params=params)
            return {"provider": self.name, "data": data}

        if self.provider == "newsapi":
            params = {"apiKey": self.api_key, "pageSize": size}
            if query:
                params["q"] = query
            if category:
                params["category"] = category
            if language:
                params["language"] = language
            data = self.get("top-headlines", params=params)
            return {"provider": self.name, "data": data}

        raise ValueError("Provider atual não suporta latest(); use from_rss para RSS.")

    def from_rss(self, feed_url: str, limit: int = 10) -> Dict[str, Any]:
        """Lê um feed RSS/Atom sem dependências externas."""
        try:
            import requests

            resp = requests.get(feed_url, timeout=15)
            resp.raise_for_status()
            content = resp.content

            # Tentativa de parse RSS/Atom simples
            root = ET.fromstring(content)
            # RSS 2.0: channel/item; Atom: feed/entry
            items: List[Dict[str, Any]] = []

            channel = root.find("channel")
            if channel is not None:
                for item in channel.findall("item")[:limit]:
                    items.append({
                        "title": (item.findtext("title") or "").strip(),
                        "link": (item.findtext("link") or "").strip(),
                        "published": (item.findtext("pubDate") or "").strip(),
                        "source": (channel.findtext("title") or "RSS").strip(),
                    })
            else:
                # Atom
                for entry in root.findall("{http://www.w3.org/2005/Atom}entry")[:limit]:
                    link_el = entry.find('{http://www.w3.org/2005/Atom}link')
                    link = link_el.get('href') if link_el is not None else ""
                    items.append({
                        "title": (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip(),
                        "link": link,
                        "published": (entry.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip(),
                        "source": (root.findtext("{http://www.w3.org/2005/Atom}title") or "Atom").strip(),
                    })

            return {"provider": "RSS", "data": {"results": items, "fetched_at": datetime.utcnow().isoformat()}}
        except Exception as e:
            logger.error(f"Erro ao ler RSS: {e}")
            return {"provider": "RSS", "data": None, "error": str(e)}

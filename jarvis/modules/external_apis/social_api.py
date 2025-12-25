#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SocialMediaAPI - Integrações simples para redes sociais (leitura/post onde possível).
Tokens devem ser fornecidos via variáveis de ambiente.

Suporte inicial:
- X (Twitter) v2: leitura de timeline do usuário (Bearer) e post por OAuth2 (tweet.write) ou OAuth1 (não implementado aqui)
- LinkedIn: criação de post usando access token (scope w_member_social)

Observação: Alguns endpoints de post exigem permissões específicas e apps aprovados.
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class SocialMediaAPI:
    def __init__(self):
        self.twitter_bearer = os.getenv("TWITTER_BEARER_TOKEN")
        self.twitter_access_token = os.getenv("TWITTER_USER_TOKEN")  # opcional para post
        self.linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.linkedin_urn = os.getenv("LINKEDIN_URN")  # ex: urn:li:person:xxxx

    # ---------- Twitter (X) ----------
    def twitter_user_timeline(self, user_id: str, max_results: int = 5) -> Dict[str, Any]:
        if not self.twitter_bearer:
            return {"provider": "twitter", "error": "TWITTER_BEARER_TOKEN ausente"}
        try:
            url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {"max_results": max_results, "tweet.fields": "created_at,public_metrics"}
            headers = {"Authorization": f"Bearer {self.twitter_bearer}"}
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "twitter", "data": resp.json()}
        except Exception as e:
            logger.error(f"Erro Twitter timeline: {e}")
            return {"provider": "twitter", "error": str(e)}

    def twitter_post_tweet(self, text: str) -> Dict[str, Any]:
        # Requer escopo tweet.write e fluxo OAuth2 adequado
        token = self.twitter_access_token or self.twitter_bearer
        if not token:
            return {"provider": "twitter", "error": "Token para postagem ausente"}
        try:
            url = "https://api.twitter.com/2/tweets"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            payload = {"text": text}
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "twitter", "data": resp.json()}
        except Exception as e:
            logger.error(f"Erro ao postar no Twitter: {e}")
            return {"provider": "twitter", "error": str(e)}

    # ---------- LinkedIn ----------
    def linkedin_post(self, text: str) -> Dict[str, Any]:
        if not self.linkedin_token or not self.linkedin_urn:
            return {"provider": "linkedin", "error": "LINKEDIN_ACCESS_TOKEN ou LINKEDIN_URN ausente"}
        try:
            url = "https://api.linkedin.com/v2/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.linkedin_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            }
            payload = {
                "author": self.linkedin_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "linkedin", "data": resp.json() if resp.text else {"status": "posted"}}
        except Exception as e:
            logger.error(f"Erro LinkedIn post: {e}")
            return {"provider": "linkedin", "error": str(e)}

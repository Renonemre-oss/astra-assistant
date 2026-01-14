#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EmailAPI - Integração mínima com Gmail e Outlook via REST.
Requer tokens OAuth fornecidos via variáveis de ambiente.

Configuração esperada:
- GMAIL_TOKEN: token OAuth Bearer válido para Gmail API
- MS_GRAPH_TOKEN: token OAuth Bearer válido para Microsoft Graph (Outlook)

Atenção: Para enviar emails no Gmail API, a mensagem deve estar em base64url.
"""

from __future__ import annotations

import os
import base64
import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class EmailAPI:
    def __init__(self):
        self.gmail_token = os.getenv("GMAIL_TOKEN")
        self.ms_token = os.getenv("MS_GRAPH_TOKEN")

    # ---------- Gmail ----------
    def gmail_list_messages(self, max_results: int = 10, query: str = "") -> Dict[str, Any]:
        if not self.gmail_token:
            return {"provider": "gmail", "error": "GMAIL_TOKEN ausente"}
        try:
            url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
            params = {"maxResults": max_results}
            if query:
                params["q"] = query
            headers = {"Authorization": f"Bearer {self.gmail_token}"}
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "gmail", "data": resp.json()}
        except Exception as e:
            logger.error(f"Erro Gmail list: {e}")
            return {"provider": "gmail", "error": str(e)}

    def gmail_send_message(self, subject: str, to: str, body_text: str) -> Dict[str, Any]:
        if not self.gmail_token:
            return {"provider": "gmail", "error": "GMAIL_TOKEN ausente"}
        try:
            raw = f"To: {to}\r\nSubject: {subject}\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n{body_text}"
            raw_b64 = base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")
            url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
            headers = {
                "Authorization": f"Bearer {self.gmail_token}",
                "Content-Type": "application/json",
            }
            payload = {"raw": raw_b64}
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "gmail", "data": resp.json()}
        except Exception as e:
            logger.error(f"Erro Gmail send: {e}")
            return {"provider": "gmail", "error": str(e)}

    # ---------- Outlook (Graph) ----------
    def outlook_list_messages(self, max_results: int = 10, search: str = "") -> Dict[str, Any]:
        if not self.ms_token:
            return {"provider": "outlook", "error": "MS_GRAPH_TOKEN ausente"}
        try:
            url = "https://graph.microsoft.com/v1.0/me/messages"
            params = {"$top": max_results}
            headers = {"Authorization": f"Bearer {self.ms_token}"}
            if search:
                # Graph usa $search com cabeçalho ConsistencyLevel: eventual
                headers["ConsistencyLevel"] = "eventual"
                params["$search"] = f'"{search}"'
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "outlook", "data": resp.json()}
        except Exception as e:
            logger.error(f"Erro Outlook list: {e}")
            return {"provider": "outlook", "error": str(e)}

    def outlook_send_message(self, subject: str, to: str, body_html: str) -> Dict[str, Any]:
        if not self.ms_token:
            return {"provider": "outlook", "error": "MS_GRAPH_TOKEN ausente"}
        try:
            url = "https://graph.microsoft.com/v1.0/me/sendMail"
            headers = {
                "Authorization": f"Bearer {self.ms_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "message": {
                    "subject": subject,
                    "body": {"contentType": "HTML", "content": body_html},
                    "toRecipients": [{"emailAddress": {"address": to}}],
                },
                "saveToSentItems": True,
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "outlook", "data": resp.json() if resp.text else {"status": "sent"}}
        except Exception as e:
            logger.error(f"Erro Outlook send: {e}")
            return {"provider": "outlook", "error": str(e)}

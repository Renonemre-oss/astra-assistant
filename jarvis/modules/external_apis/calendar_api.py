#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CalendarAPI - Integração mínima com Google Calendar e Microsoft Outlook (Graph).
Requer tokens OAuth fornecidos pelo usuário (não gerencia fluxo de OAuth).

Configuração esperada (variáveis de ambiente):
- GOOGLE_CALENDAR_TOKEN: token OAuth Bearer válido para Google Calendar
- MS_GRAPH_TOKEN: token OAuth Bearer válido para Microsoft Graph
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class CalendarAPI:
    def __init__(self):
        self.google_token = os.getenv("GOOGLE_CALENDAR_TOKEN")
        self.ms_token = os.getenv("MS_GRAPH_TOKEN")

    # ---------- Google Calendar ----------
    def google_list_events(self, max_results: int = 10) -> Dict[str, Any]:
        if not self.google_token:
            return {"provider": "google", "error": "GOOGLE_CALENDAR_TOKEN ausente"}
        try:
            time_min = datetime.now(timezone.utc).isoformat()
            url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            params = {
                "maxResults": max_results,
                "orderBy": "startTime",
                "singleEvents": "true",
                "timeMin": time_min,
            }
            headers = {"Authorization": f"Bearer {self.google_token}"}
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "google", "data": resp.json()}
        except Exception as e:
            logger.error(f"Erro Google Calendar: {e}")
            return {"provider": "google", "error": str(e)}

    def google_create_event(self, summary: str, start_iso: str, end_iso: str, description: str = "") -> Dict[str, Any]:
        if not self.google_token:
            return {"provider": "google", "error": "GOOGLE_CALENDAR_TOKEN ausente"}
        try:
            url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
            headers = {
                "Authorization": f"Bearer {self.google_token}",
                "Content-Type": "application/json",
            }
            body = {
                "summary": summary,
                "description": description,
                "start": {"dateTime": start_iso},
                "end": {"dateTime": end_iso},
            }
            resp = requests.post(url, json=body, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "google", "data": resp.json()}
        except Exception as e:
            logger.error(f"Erro ao criar evento Google: {e}")
            return {"provider": "google", "error": str(e)}

    # ---------- Microsoft Outlook (Graph) ----------
    def outlook_list_events(self, max_results: int = 10) -> Dict[str, Any]:
        if not self.ms_token:
            return {"provider": "outlook", "error": "MS_GRAPH_TOKEN ausente"}
        try:
            url = "https://graph.microsoft.com/v1.0/me/events"
            params = {"$top": max_results, "$orderby": "start/dateTime"}
            headers = {"Authorization": f"Bearer {self.ms_token}"}
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "outlook", "data": resp.json()}
        except Exception as e:
            logger.error(f"Erro Outlook: {e}")
            return {"provider": "outlook", "error": str(e)}

    def outlook_create_event(self, subject: str, start_iso: str, end_iso: str, body: str = "") -> Dict[str, Any]:
        if not self.ms_token:
            return {"provider": "outlook", "error": "MS_GRAPH_TOKEN ausente"}
        try:
            url = "https://graph.microsoft.com/v1.0/me/events"
            headers = {
                "Authorization": f"Bearer {self.ms_token}",
                "Content-Type": "application/json",
            }
            body_json = {
                "subject": subject,
                "body": {"contentType": "HTML", "content": body},
                "start": {"dateTime": start_iso, "timeZone": "UTC"},
                "end": {"dateTime": end_iso, "timeZone": "UTC"},
            }
            resp = requests.post(url, json=body_json, headers=headers, timeout=20)
            resp.raise_for_status()
            return {"provider": "outlook", "data": resp.json()}
        except Exception as e:
            logger.error(f"Erro ao criar evento Outlook: {e}")
            return {"provider": "outlook", "error": str(e)}

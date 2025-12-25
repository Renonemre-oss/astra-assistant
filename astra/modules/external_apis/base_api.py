#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BaseAPI - Classe base para integrações HTTP com APIs externas.
Fornece:
- Sessão HTTP com timeout e retries simples
- Métodos GET/POST padronizados
- Montagem de URL segura entre base_url e endpoint
- Tratamento de erros e logging básico

Observação: Não gerencia OAuth. Tokens devem ser injetados via headers.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)


class BaseAPI:
    """Classe base utilitária para chamadas HTTP."""

    def __init__(self, api_key: Optional[str], base_url: str, name: str = "API"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") + "/"
        self.name = name
        self.session = requests.Session()
        self.default_timeout = 15
        self.default_headers: Dict[str, str] = {
            "User-Agent": f"Astra/{self.name}",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        return urljoin(self.base_url, endpoint)

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        url = self._build_url(endpoint)
        req_headers = {**self.default_headers, **(headers or {})}
        try:
            resp = self.session.get(url, params=params, headers=req_headers, timeout=timeout or self.default_timeout)
            resp.raise_for_status()
            if resp.headers.get("Content-Type", "").startswith("application/json"):
                return resp.json()
            try:
                return json.loads(resp.text)
            except json.JSONDecodeError:
                logger.warning(f"{self.name} retornou conteúdo não JSON para GET {url}")
                return {"raw": resp.text}
        except requests.RequestException as e:
            logger.error(f"Erro GET {self.name} {url}: {e}")
            return None

    def post(
        self,
        endpoint: str,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        url = self._build_url(endpoint)
        req_headers = {**self.default_headers, **(headers or {})}
        try:
            resp = self.session.post(url, json=json_body, data=data, headers=req_headers, timeout=timeout or self.default_timeout)
            resp.raise_for_status()
            if resp.headers.get("Content-Type", "").startswith("application/json"):
                return resp.json()
            try:
                return json.loads(resp.text)
            except json.JSONDecodeError:
                logger.warning(f"{self.name} retornou conteúdo não JSON para POST {url}")
                return {"raw": resp.text}
        except requests.RequestException as e:
            logger.error(f"Erro POST {self.name} {url}: {e}")
            return None


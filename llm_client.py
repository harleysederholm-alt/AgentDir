"""
AgentDir – LLM Client
Tukee mitä tahansa OpenAI-yhteensopivaa paikallista serveriä.
Automaattinen fallback-malli jos päämalli ei vastaa.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import requests

logger = logging.getLogger("agentdir.llm")


class LLMClient:
    def __init__(self, config: dict):
        self.cfg = config.get("llm", {})
        self.endpoint = self.cfg.get("endpoint", "http://localhost:11434/v1/chat/completions")
        self.model = self.cfg.get("model", "llama3.2:3b")
        self.fallbacks = self.cfg.get("fallback_models", [])
        self.temperature = self.cfg.get("temperature", 0.7)
        self.max_tokens = self.cfg.get("max_tokens", 4096)
        self.timeout = self.cfg.get("timeout", 180)

    def complete(self, prompt: str, system: str | None = None) -> str:
        """
        Lähettää promptin LLM:lle ja palauttaa vastauksen.
        Yrittää fallback-malleja jos päämalli epäonnistuu.
        """
        models_to_try = [self.model] + self.fallbacks

        for model in models_to_try:
            try:
                result = self._call(model, prompt, system)
                if result:
                    return result
            except requests.exceptions.ConnectionError:
                logger.error(
                    "LLM ei saatavilla (%s) – onko Ollama käynnissä? (ollama serve)", model
                )
                if model == models_to_try[-1]:
                    return "❌ LLM-yhteysvirhe: Varmista että Ollama on käynnissä komennolla 'ollama serve'"
            except Exception as e:
                logger.warning("Malli '%s' epäonnistui: %s – kokeillaan seuraavaa", model, e)

        return "❌ Kaikki LLM-mallit epäonnistuivat."

    def _call(self, model: str, prompt: str, system: str | None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }

        resp = requests.post(self.endpoint, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def complete_json(self, prompt: str, system: str | None = None) -> dict | None:
        """
        Kuten complete(), mutta parsii JSON-vastauksen automaattisesti.
        Palauttaa None jos parsing epäonnistuu.
        """
        raw = self.complete(prompt, system)
        # Etsi JSON-rakenne vastauksesta
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if not match:
            logger.warning("LLM ei palauttanut JSONia: %s...", raw[:200])
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            logger.warning("JSON-parsaus epäonnistui: %s", e)
            return None

    def check_connection(self) -> bool:
        """Tarkista että LLM-serveri vastaa."""
        try:
            resp = requests.get(
                self.endpoint.replace("/v1/chat/completions", "/v1/models"),
                timeout=5
            )
            return resp.status_code == 200
        except Exception:
            return False

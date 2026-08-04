"""
Thin async wrapper around the local Ollama HTTP API.
No cloud API keys are used anywhere in this module -- everything runs against
a locally running `ollama serve` instance (default http://localhost:11434).
"""
from typing import Optional

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClient:
    def __init__(
        self,
        base_url: str = settings.ollama_base_url,
        model: str = settings.ollama_model,
        temperature: float = settings.ollama_temperature,
        timeout: float = 120.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    async def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Single-shot text generation using /api/generate."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "",
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()

    async def chat(self, messages: list[dict], system: Optional[str] = None) -> str:
        """Multi-turn chat using /api/chat. messages = [{"role": "user", "content": "..."}]"""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": full_messages,
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "").strip()

    async def is_reachable(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Ollama not reachable: {exc}")
            return False


# Shared singleton instance used throughout the app
ollama_client = OllamaClient()

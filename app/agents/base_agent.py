"""
Abstract base class all specialized agents inherit from.
Provides a shared LLM client and a common `run` interface.
"""
from abc import ABC, abstractmethod

from app.llm.ollama_client import ollama_client
from app.utils.logger import get_logger


class BaseAgent(ABC):
    name: str = "base_agent"
    system_prompt: str = "You are a helpful AI agent."

    def __init__(self):
        self.llm = ollama_client
        self.logger = get_logger(f"agent.{self.name}")

    @abstractmethod
    async def run(self, state: dict) -> dict:
        """Given the current workflow state dict, return updated state fields."""
        raise NotImplementedError

    async def _ask(self, prompt: str) -> str:
        self.logger.info(f"Prompting local LLM ({self.llm.model})...")
        return await self.llm.generate(prompt=prompt, system=self.system_prompt)

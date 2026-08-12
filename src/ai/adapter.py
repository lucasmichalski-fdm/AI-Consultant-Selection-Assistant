"""LLM adapter interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LlmAdapter(ABC):
    """Abstract interface for explanation generation."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate raw model text from prompt."""
        raise NotImplementedError

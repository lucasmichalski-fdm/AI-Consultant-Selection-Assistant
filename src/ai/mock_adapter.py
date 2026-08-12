"""Deterministic mock adapter for offline development."""

from __future__ import annotations

from src.ai.adapter import LlmAdapter


class MockAdapter(LlmAdapter):
    """A predictable adapter used in tests and local runs."""

    def generate(self, prompt: str) -> str:
        return '{"rationale":"Mock rationale generated from provided evidence.","confidence":0.75,"prompt_chars":%d}' % len(prompt)

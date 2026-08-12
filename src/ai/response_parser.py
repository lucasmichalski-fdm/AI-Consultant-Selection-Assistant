"""Model response parsing stubs."""

from __future__ import annotations

import json
from typing import Any


def parse_model_response(raw_text: str) -> dict[str, Any]:
    """Parse JSON model output with fallback metadata."""

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            return parsed
        return {"rationale": str(parsed), "confidence": 0.5, "limitations": ["non_object_json"]}
    except json.JSONDecodeError:
        return {
            "rationale": "Fallback rationale: parser could not decode model output.",
            "confidence": 0.4,
            "limitations": ["parse_error"],
        }

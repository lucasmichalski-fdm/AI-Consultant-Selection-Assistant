"""CSV loading utilities for dataset files."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def _load_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing dataset file: {path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def load_consultants_csv(path: Path) -> list[dict[str, Any]]:
    """Load raw consultant profile rows."""

    return _load_csv(path)


def load_roles_csv(path: Path) -> list[dict[str, Any]]:
    """Load raw role requirement rows."""

    return _load_csv(path)


def load_historical_matches_csv(path: Path) -> list[dict[str, Any]]:
    """Load historical matching rows for later evaluation milestones."""

    return _load_csv(path)

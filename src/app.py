"""CLI entry point for Milestone A validation."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import RankingPipeline


def main() -> None:
    snapshot = RankingPipeline(project_root=ROOT).run_milestone_a_snapshot()
    print(json.dumps(snapshot.__dict__, indent=2))


if __name__ == "__main__":
    main()

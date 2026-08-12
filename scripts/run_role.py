"""Run Milestone A snapshot for a single role-oriented flow."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from dataclasses import asdict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import RankingPipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role-id", required=False, default="R-001")
    parser.add_argument("--top-n", required=False, type=int, default=5)
    parser.add_argument("--retrieve-k", required=False, type=int, default=25)
    args = parser.parse_args()

    result = RankingPipeline(project_root=ROOT).run_milestone_b_for_role(
        role_id=args.role_id,
        top_n=args.top_n,
        retrieve_k=args.retrieve_k,
    )

    payload = {"milestone": "B", **asdict(result)}
    output_dir = ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{timestamp}.json"
    output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"\nWrote output file: {output_file}")


if __name__ == "__main__":
    main()

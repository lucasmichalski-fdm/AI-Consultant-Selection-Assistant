"""Batch-run placeholder for all roles."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from dataclasses import asdict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io.data_loader import load_roles_csv
from src.pipeline import RankingPipeline


def main() -> None:
    pipeline = RankingPipeline(project_root=ROOT)
    roles = load_roles_csv(ROOT / "dataset" / "role_requirements_train.csv")

    runs = []
    total = 0
    with_constraints_in_top5 = 0
    avg_top1 = 0.0

    for role in roles:
        role_id = role.get("role_id", "")
        if not role_id:
            continue

        result = pipeline.run_milestone_b_for_role(role_id=role_id)
        payload = asdict(result)
        runs.append(payload)
        total += 1

        if payload["ranked_candidates"]:
            avg_top1 += payload["ranked_candidates"][0]["fit_score"]

        top5 = payload["ranked_candidates"][:5]
        if any(candidate["risk_flags"] for candidate in top5):
            with_constraints_in_top5 += 1

    summary = {
        "runs": total,
        "avg_top1_fit_score": round(avg_top1 / total, 2) if total else 0.0,
        "roles_with_constraint_flags_in_top5": with_constraints_in_top5,
        "sample": runs[:3],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

"""HTTP API for the consultant ranking MVP (file-based, no database)."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.io.data_loader import load_roles_csv
from src.pipeline import RankingPipeline
from src.scoring.policy import RankingPolicy


class PolicyToggles(BaseModel):
    locationMode: Literal["hard", "soft", "ignore"] = "hard"
    enforceOfficeSchedule: bool = True
    allowRelocationPath: bool = True
    startDateMode: Literal["hard", "soft", "ignore"] = "hard"
    authorizationMode: Literal["hard", "soft", "ignore"] = "hard"
    experienceMode: Literal["hard", "soft", "ignore"] = "hard"
    certificationMode: Literal["hard", "soft", "ignore"] = "soft"
    domainMode: Literal["hard", "soft", "ignore"] = "soft"


class RankRequest(BaseModel):
    role_id: str = Field(min_length=1)
    top_n: int = Field(default=5, ge=1, le=20)
    retrieve_k: int = Field(default=25, ge=5, le=200)
    policy: PolicyToggles = Field(default_factory=PolicyToggles)
    save_output: bool = False


def _to_ranking_policy(policy: PolicyToggles) -> RankingPolicy:
    return RankingPolicy.from_mapping(policy.model_dump())


def create_app(project_root: Path | None = None) -> FastAPI:
    root = project_root or Path(__file__).resolve().parents[2]
    pipeline = RankingPipeline(project_root=root)

    app = FastAPI(
        title="AI Consultant Selection Assistant API",
        version="0.1.0",
        description="File-based ranking API for hackathon use. No database required.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    output_dir = root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    def _save_payload(payload: dict) -> Path:
        request_id = payload.get("request_id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = output_dir / f"{timestamp}_{request_id}.json"
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return out_path

    def _find_saved_run(request_id: str) -> dict | None:
        for file_path in sorted(output_dir.glob("*.json"), reverse=True):
            try:
                raw = json.loads(file_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if raw.get("request_id") == request_id:
                return raw
        return None

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "file-backed"}

    @app.get("/roles")
    def list_roles() -> list[dict[str, str]]:
        rows = load_roles_csv(root / "dataset" / "role_requirements_train.csv")
        return [
            {
                "id": row.get("role_id", ""),
                "title": row.get("role_title", ""),
                "location": f"{row.get('location_city', '')}, {row.get('location_state', '')}",
                "mode": row.get("remote_or_onsite", ""),
            }
            for row in rows
            if row.get("role_id")
        ]

    @app.post("/rank")
    def rank(request: RankRequest) -> dict:
        ranking_policy = _to_ranking_policy(request.policy)
        try:
            result = pipeline.run_milestone_b_for_role(
                role_id=request.role_id,
                top_n=request.top_n,
                retrieve_k=request.retrieve_k,
                policy=ranking_policy,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        payload = {
            "milestone": "B",
            **asdict(result),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "applied_policy": request.policy.model_dump(),
        }

        if request.save_output:
            out_path = _save_payload(payload)
            payload["saved_path"] = str(out_path)

        return payload

    @app.post("/rank/save")
    def rank_and_save(request: RankRequest) -> dict:
        request.save_output = True
        return rank(request)

    @app.get("/runs/{request_id}")
    def get_saved_run(request_id: str) -> dict:
        payload = _find_saved_run(request_id)
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Run not found for request_id={request_id}")
        return payload

    @app.get("/runs")
    def list_saved_runs(limit: int = 20) -> list[dict]:
        runs: list[dict] = []
        for file_path in sorted(output_dir.glob("*.json"), reverse=True):
            try:
                raw = json.loads(file_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if "request_id" not in raw:
                continue
            runs.append(
                {
                    "request_id": raw.get("request_id"),
                    "role_id": raw.get("role_id"),
                    "generated_at": raw.get("generated_at"),
                    "top_n": raw.get("top_n"),
                }
            )
            if len(runs) >= limit:
                break
        return runs

    return app


app = create_app()

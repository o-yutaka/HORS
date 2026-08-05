from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from capability.skill_lift.run import main
from capability.skill_lift.workspace_ports import JsonlEvaluationPort


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _candidate(candidate_id: str) -> dict:
    return {
        "id": candidate_id,
        "hypothesis_id": "scoped-intervention",
        "track": "static",
        "skills": [
            {
                "name": "bounded-task-execution",
                "description": "Execute only authorized task-scoped actions and verify resulting state.",
                "body": "## When to use this skill\n- Multi-step tool tasks.\n\n## Procedure\n1. Confirm scope.\n2. Act minimally.\n3. Verify state.",
                "scripts": {},
                "references": {},
            }
        ],
        "components": ["scope-gate", "minimal-action", "state-verification"],
        "provenance": ["public SkillsBench evidence"],
        "estimated_tokens": 220,
        "compliance_flags": [],
    }


def _trial(task: str, variant: str, score: float, domain: str, *, held_out: bool = False) -> dict:
    return {
        "task_id": task,
        "variant_id": variant,
        "seed": 1,
        "score": score,
        "safety": 1.0,
        "tokens": 900 if variant == "baseline" else 860,
        "latency_ms": 100,
        "domain": domain,
        "model_id": "model-a",
        "run_index": 0,
        "held_out": held_out,
        "safety_violation": None,
    }


def test_cli_reaches_frozen_exact_submission(tmp_path: Path) -> None:
    candidate = _candidate("candidate-a")
    recomposed = _candidate("skill-recomposed")
    _write_json(tmp_path / "private/candidates/static/candidate-a.json", candidate)
    _write_json(tmp_path / "private/recomposed/static.json", recomposed)

    _write_jsonl(
        tmp_path / "evidence/baseline.jsonl",
        [
            _trial("task-1", "baseline", 0.40, "docs"),
            _trial("task-2", "baseline", 0.45, "calendar"),
        ],
    )
    _write_jsonl(
        tmp_path / "evidence/arena.jsonl",
        [
            _trial("task-1", "candidate-a", 0.70, "docs"),
            _trial("task-2", "candidate-a", 0.65, "calendar"),
        ],
    )
    _write_jsonl(
        tmp_path / "evidence/held_out.jsonl",
        [
            _trial("held-1", "baseline", 0.35, "slack", held_out=True),
            _trial("held-2", "baseline", 0.40, "drive", held_out=True),
            _trial("held-1", "skill-recomposed", 0.62, "slack", held_out=True),
            _trial("held-2", "skill-recomposed", 0.58, "drive", held_out=True),
        ],
    )

    exit_code = main(
        [
            "--workspace",
            str(tmp_path),
            "--track",
            "static",
            "--run-id",
            "static-final",
            "--confirm-active-deadline",
            "--confirm-submission-limit",
            "--confirm-kaggle-public-code-disclosure",
        ]
    )
    assert exit_code == 0

    output = tmp_path / "runs/static-final"
    submissions = list(output.glob("submission-static-*.zip"))
    assert len(submissions) == 1
    with zipfile.ZipFile(submissions[0]) as archive:
        assert archive.namelist() == ["skills/bounded-task-execution/SKILL.md"]
    assert (output / "WRITEUP-static.md").exists()
    assert (output / "submission-manifest.json").exists()
    assert list(output.glob("audit-static-*.zip"))


def test_duplicate_measured_trial_identity_is_rejected(tmp_path: Path) -> None:
    row = _trial("task-1", "baseline", 0.40, "docs")
    _write_jsonl(tmp_path / "baseline.jsonl", [row, row])
    with pytest.raises(RuntimeError, match="DUPLICATE_TRIAL_IDENTITY"):
        JsonlEvaluationPort(tmp_path).baseline(None)  # type: ignore[arg-type]

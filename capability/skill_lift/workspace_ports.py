from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from capability.competition_operator import (
    CandidateSkill,
    CompetitionRun,
    CompetitionTrack,
    Hypothesis,
    SafetySeverity,
    SkillDocument,
    TrialResult,
)


class SkillLiftHypothesisGenerator:
    """Produces track-aware hypotheses from the official contract, not private tasks."""

    def generate(self, official: dict[str, Any]) -> list[Hypothesis]:
        public = official["evaluation"]["public_corpus"]
        return [
            Hypothesis(
                id="scoped-intervention",
                claim="Explicit applicability and stop conditions reduce the public regression tail while preserving lift.",
                expected_lift=0.10,
                risks=("under-triggering", "overly conservative execution"),
                evidence_ids=(public,),
            ),
            Hypothesis(
                id="state-verification",
                claim="Pre-action authority checks and post-action state verification improve agentic task reliability and safety.",
                expected_lift=0.12,
                risks=("extra instruction load", "redundant verification"),
                evidence_ids=("ClawsBench safety surface",),
            ),
            Hypothesis(
                id="feedback-bounded-meta-optimization",
                claim="A meta-skill that edits only evidenced failure modes can improve calibration lift without producing unsafe broad skills.",
                expected_lift=0.15,
                risks=("calibration overfit", "skill bloat", "unsafe self-modification"),
                evidence_ids=("meta evolution contract",),
            ),
        ]


class SkillLiftAssetMiner:
    """Returns only the official public resources declared in the contract."""

    def search(self, official: dict[str, Any], hypotheses: list[Hypothesis]) -> list[dict[str, Any]]:
        return list(official.get("recommended_assets", []))


def _document(payload: dict[str, Any]) -> SkillDocument:
    return SkillDocument(
        name=str(payload["name"]),
        description=str(payload["description"]),
        body=str(payload["body"]),
        scripts={str(key): str(value) for key, value in payload.get("scripts", {}).items()},
        references={str(key): str(value) for key, value in payload.get("references", {}).items()},
    )


def _candidate(payload: dict[str, Any]) -> CandidateSkill:
    return CandidateSkill(
        id=str(payload["id"]),
        hypothesis_id=str(payload["hypothesis_id"]),
        track=CompetitionTrack(str(payload["track"])),
        skills=tuple(_document(item) for item in payload["skills"]),
        components=tuple(str(value) for value in payload.get("components", [])),
        provenance=tuple(str(value) for value in payload.get("provenance", [])),
        estimated_tokens=int(payload.get("estimated_tokens", 0)),
        compliance_flags=tuple(str(value) for value in payload.get("compliance_flags", [])),
    )


class PrivateWorkspaceSkillPort:
    """Loads BLACK-generated skills from a gitignored private workspace."""

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace)

    def generate(self, run: CompetitionRun) -> list[CandidateSkill]:
        root = self.workspace / "candidates" / run.track.value
        if not root.exists():
            raise RuntimeError(f"PRIVATE_CANDIDATE_DIRECTORY_MISSING:{root}")
        candidates = [_candidate(json.loads(path.read_text(encoding="utf-8"))) for path in sorted(root.glob("*.json"))]
        if not candidates:
            raise RuntimeError(f"PRIVATE_CANDIDATES_MISSING:{root}")
        return candidates

    def recompose(self, run: CompetitionRun, components: list[str]) -> CandidateSkill:
        path = self.workspace / "recomposed" / f"{run.track.value}.json"
        if not path.exists():
            raise RuntimeError(f"PRIVATE_RECOMPOSED_CANDIDATE_MISSING:{path}")
        candidate = _candidate(json.loads(path.read_text(encoding="utf-8")))
        missing = sorted(set(components) - set(candidate.components))
        if missing:
            raise RuntimeError(f"RECOMPOSITION_DROPPED_WINNING_COMPONENTS:{','.join(missing)}")
        return candidate


def _trial(payload: dict[str, Any]) -> TrialResult:
    violation = payload.get("safety_violation")
    return TrialResult(
        task_id=str(payload["task_id"]),
        variant_id=str(payload["variant_id"]),
        seed=int(payload["seed"]),
        score=float(payload["score"]),
        safety=float(payload.get("safety", 1.0)),
        tokens=int(payload.get("tokens", 0)),
        latency_ms=int(payload.get("latency_ms", 0)),
        domain=str(payload.get("domain", "unknown")),
        model_id=str(payload.get("model_id", "unknown")),
        run_index=int(payload.get("run_index", 0)),
        held_out=bool(payload.get("held_out", False)),
        safety_violation=SafetySeverity(str(violation)) if violation else None,
    )


class JsonlEvaluationPort:
    """Consumes measured Kaggle/BenchFlow evidence and refuses to invent missing trials."""

    def __init__(self, evidence_root: str | Path) -> None:
        self.evidence_root = Path(evidence_root)

    def _read(self, name: str) -> list[TrialResult]:
        path = self.evidence_root / name
        if not path.exists():
            raise RuntimeError(f"MEASURED_EVIDENCE_MISSING:{path}")
        trials = [
            _trial(json.loads(line))
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not trials:
            raise RuntimeError(f"MEASURED_EVIDENCE_EMPTY:{path}")
        identities = [(trial.variant_id, trial.pair_key) for trial in trials]
        if len(identities) != len(set(identities)):
            raise RuntimeError(f"DUPLICATE_TRIAL_IDENTITY:{path}")
        return trials

    def baseline(self, run: CompetitionRun) -> list[TrialResult]:
        trials = self._read("baseline.jsonl")
        if any(trial.variant_id != "baseline" or trial.held_out for trial in trials):
            raise RuntimeError("BASELINE_EVIDENCE_CONTRACT_INVALID")
        return trials

    def arena(self, run: CompetitionRun, candidates: list[CandidateSkill]) -> list[TrialResult]:
        trials = self._read("arena.jsonl")
        allowed = {candidate.id for candidate in candidates}
        if any(trial.variant_id not in allowed or trial.held_out for trial in trials):
            raise RuntimeError("ARENA_EVIDENCE_CONTRACT_INVALID")
        return trials

    def held_out(self, run: CompetitionRun, candidate: CandidateSkill) -> list[TrialResult]:
        trials = self._read("held_out.jsonl")
        allowed = {"baseline", candidate.id}
        if any(trial.variant_id not in allowed or not trial.held_out for trial in trials):
            raise RuntimeError("HELD_OUT_EVIDENCE_CONTRACT_INVALID")
        if {trial.variant_id for trial in trials} != allowed:
            raise RuntimeError("HELD_OUT_REQUIRES_PAIRED_BASELINE_AND_CANDIDATE")
        return trials

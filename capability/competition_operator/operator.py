from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Protocol

from .contracts import (
    ArenaVerdict,
    CandidateSkill,
    CompetitionRun,
    Evidence,
    FrozenSubmission,
    Hypothesis,
    RunStage,
    TrialResult,
)


class OfficialIntelligencePort(Protocol):
    def collect(self, competition_url: str) -> dict[str, Any]: ...


class HypothesisPort(Protocol):
    def generate(self, official: dict[str, Any]) -> list[Hypothesis]: ...


class AssetMiningPort(Protocol):
    def search(self, official: dict[str, Any], hypotheses: list[Hypothesis]) -> list[dict[str, Any]]: ...


class NotebookPort(Protocol):
    def generate(self, run: CompetitionRun, output_dir: Path) -> str: ...


class SkillPort(Protocol):
    def generate(self, run: CompetitionRun) -> list[CandidateSkill]: ...
    def recompose(self, run: CompetitionRun, components: list[str]) -> CandidateSkill: ...


class EvaluationPort(Protocol):
    def baseline(self, run: CompetitionRun) -> list[TrialResult]: ...
    def arena(self, run: CompetitionRun, candidates: list[CandidateSkill]) -> list[TrialResult]: ...
    def held_out(self, run: CompetitionRun, candidate: CandidateSkill) -> list[TrialResult]: ...


class FreezePort(Protocol):
    def freeze(self, run: CompetitionRun, candidate: CandidateSkill, output_dir: Path) -> FrozenSubmission: ...


class OperatorPorts:
    def __init__(
        self,
        official: OfficialIntelligencePort,
        hypotheses: HypothesisPort,
        assets: AssetMiningPort,
        notebooks: NotebookPort,
        skills: SkillPort,
        evaluation: EvaluationPort,
        freezer: FreezePort,
    ) -> None:
        self.official = official
        self.hypotheses = hypotheses
        self.assets = assets
        self.notebooks = notebooks
        self.skills = skills
        self.evaluation = evaluation
        self.freezer = freezer


def _digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("empty aggregate")
    return sum(values) / len(values)


def _judge(trials: list[TrialResult], baseline_id: str = "baseline") -> ArenaVerdict:
    grouped: dict[str, list[TrialResult]] = {}
    for trial in trials:
        if not trial.held_out:
            grouped.setdefault(trial.variant_id, []).append(trial)
    baseline = grouped.get(baseline_id)
    if not baseline:
        raise ValueError("baseline trials are required")
    b_score = _mean([x.score for x in baseline])
    b_safety = _mean([x.safety for x in baseline])
    b_tokens = round(_mean([float(x.tokens) for x in baseline]))
    ranked: list[tuple[float, float, int, str]] = []
    for variant, rows in grouped.items():
        if variant == baseline_id:
            continue
        ranked.append((
            _mean([x.score for x in rows]) - b_score,
            _mean([x.safety for x in rows]) - b_safety,
            b_tokens - round(_mean([float(x.tokens) for x in rows])),
            variant,
        ))
    if not ranked:
        raise ValueError("candidate trials are required")
    lift, safety_delta, token_delta, winner = max(ranked, key=lambda x: (x[0], x[1], x[2]))
    reasons: list[str] = []
    if lift <= 0:
        reasons.append("NO_CAPABILITY_LIFT")
    if safety_delta < 0:
        reasons.append("SAFETY_REGRESSION")
    if token_delta < -500:
        reasons.append("EXCESSIVE_TOKEN_COST")
    return ArenaVerdict(winner, lift, safety_delta, token_delta, not reasons, tuple(reasons))


class CompetitionOperator:
    """Resumable BLACK-controlled pipeline from competition URL to frozen package."""

    def __init__(self, ports: OperatorPorts, workspace: str | Path) -> None:
        self.ports = ports
        self.workspace = Path(workspace)

    def _record(self, run: CompetitionRun, stage: RunStage, source: str, payload: Any) -> None:
        run.stage = stage
        run.evidence.append(Evidence(stage, source, _digest(payload), payload if isinstance(payload, dict) else {"value": payload}))
        self._checkpoint(run)

    def _checkpoint(self, run: CompetitionRun) -> None:
        target = self.workspace / run.run_id
        target.mkdir(parents=True, exist_ok=True)
        (target / "run.json").write_text(json.dumps(asdict(run), indent=2, default=str), encoding="utf-8")

    def execute(self, run: CompetitionRun) -> CompetitionRun:
        out = self.workspace / run.run_id
        try:
            official = self.ports.official.collect(run.competition_url)
            required = {"title", "rules", "evaluation", "submission"}
            missing = sorted(required - set(official))
            if missing:
                raise RuntimeError(f"OFFICIAL_INTELLIGENCE_INCOMPLETE:{','.join(missing)}")
            self._record(run, RunStage.OFFICIAL_INTELLIGENCE, "official", official)

            run.hypotheses = self.ports.hypotheses.generate(official)
            if not run.hypotheses:
                raise RuntimeError("NO_WINNING_HYPOTHESIS")
            self._record(run, RunStage.WINNING_HYPOTHESIS, "hypothesis_generator", {"count": len(run.hypotheses)})

            run.assets = self.ports.assets.search(official, run.hypotheses)
            self._record(run, RunStage.ASSET_MINING, "github_asset_miner", {"assets": run.assets})

            notebook_path = self.ports.notebooks.generate(run, out)
            self._record(run, RunStage.NOTEBOOK_GENERATION, "notebook_generator", {"path": notebook_path})

            run.trials.extend(self.ports.evaluation.baseline(run))
            self._record(run, RunStage.BASELINE_EXECUTION, "kaggle_notebook", {"baseline_trials": len(run.trials)})

            run.candidates = self.ports.skills.generate(run)
            if not run.candidates:
                raise RuntimeError("NO_SKILL_CANDIDATES")
            self._record(run, RunStage.SKILL_GENERATION, "skill_generator", {"count": len(run.candidates)})

            run.trials.extend(self.ports.evaluation.arena(run, run.candidates))
            self._record(run, RunStage.ARENA, "multi_seed_arena", {"trials": len(run.trials)})

            run.verdict = _judge(run.trials)
            self._record(run, RunStage.JUDGMENT, "constitutional_judge", asdict(run.verdict))

            winner = next(x for x in run.candidates if x.id == run.verdict.winner_id)
            run.extracted_components = list(winner.components)
            self._record(run, RunStage.COMPONENT_EXTRACTION, "component_extractor", {"components": run.extracted_components})

            recomposed = self.ports.skills.recompose(run, run.extracted_components)
            run.candidates.append(recomposed)
            self._record(run, RunStage.RECOMPOSITION, "recomposer", {"candidate": recomposed.id})

            held_out = self.ports.evaluation.held_out(run, recomposed)
            run.trials.extend(held_out)
            if not held_out or _mean([x.score for x in held_out]) <= 0:
                raise RuntimeError("HELD_OUT_VERIFICATION_FAILED")
            if min(x.safety for x in held_out) < 1.0:
                raise RuntimeError("HELD_OUT_SAFETY_REGRESSION")
            self._record(run, RunStage.HELD_OUT_VERIFICATION, "held_out_verifier", {"trials": len(held_out)})

            run.frozen = self.ports.freezer.freeze(run, recomposed, out)
            self._record(run, RunStage.FROZEN, "submission_freezer", asdict(run.frozen))
            return run
        except Exception as exc:
            run.stage = RunStage.BLOCKED
            run.blocked_reason = str(exc)
            self._checkpoint(run)
            return run

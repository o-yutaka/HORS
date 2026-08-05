from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Protocol

from .contracts import (
    ArenaVerdict,
    CandidateSkill,
    CompetitionRun,
    Evidence,
    FrozenSubmission,
    Hypothesis,
    RunStage,
    SafetySeverity,
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


def _validate_official(official: dict[str, Any], track: str) -> None:
    required = {"title", "rules", "evaluation", "submission", "deadline", "tracks", "rubric"}
    missing = sorted(required - set(official))
    if missing:
        raise RuntimeError(f"OFFICIAL_INTELLIGENCE_INCOMPLETE:{','.join(missing)}")
    if track not in official["tracks"]:
        raise RuntimeError(f"TRACK_NOT_SUPPORTED:{track}")
    rubric = official["rubric"]
    required_weights = {"lift", "compliance_safety", "generalization", "writeup"}
    if set(rubric) != required_weights:
        raise RuntimeError("RUBRIC_CONTRACT_INVALID")
    if abs(sum(float(value) for value in rubric.values()) - 1.0) > 1e-9:
        raise RuntimeError("RUBRIC_WEIGHTS_DO_NOT_SUM_TO_ONE")
    submission = official["submission"]
    if submission.get("skills_root") != "skills/":
        raise RuntimeError("SUBMISSION_ROOT_MUST_BE_SKILLS")
    if not submission.get("writeup_required"):
        raise RuntimeError("WRITEUP_REQUIRED_BY_OFFICIAL_CONTRACT")


def _validate_candidate(candidate: CandidateSkill, expected_track: str) -> None:
    if candidate.track.value != expected_track:
        raise RuntimeError(f"CANDIDATE_TRACK_MISMATCH:{candidate.id}")
    if not candidate.skills:
        raise RuntimeError(f"EMPTY_SKILL_LIBRARY:{candidate.id}")
    names = [skill.name for skill in candidate.skills]
    if len(names) != len(set(names)):
        raise RuntimeError(f"DUPLICATE_SKILL_NAME:{candidate.id}")
    for skill in candidate.skills:
        if not skill.name.strip() or not skill.description.strip() or not skill.body.strip():
            raise RuntimeError(f"INVALID_SKILL_DOCUMENT:{candidate.id}:{skill.name}")


def _judge(
    trials: list[TrialResult],
    candidates: list[CandidateSkill],
    *,
    baseline_id: str = "baseline",
    held_out: bool = False,
) -> ArenaVerdict:
    scoped = [trial for trial in trials if trial.held_out is held_out]
    baseline_rows = [trial for trial in scoped if trial.variant_id == baseline_id]
    if not baseline_rows:
        raise ValueError("baseline trials are required")
    baseline = {trial.pair_key: trial for trial in baseline_rows}
    candidate_map = {candidate.id: candidate for candidate in candidates}
    verdicts: list[ArenaVerdict] = []

    for variant_id, candidate in candidate_map.items():
        variant = {trial.pair_key: trial for trial in scoped if trial.variant_id == variant_id}
        common = sorted(set(baseline) & set(variant))
        if not common:
            continue
        lifts = [variant[key].score - baseline[key].score for key in common]
        safety_deltas = [variant[key].safety - baseline[key].safety for key in common]
        token_deltas = [baseline[key].tokens - variant[key].tokens for key in common]
        domain_lifts: dict[str, list[float]] = {}
        for key in common:
            domain_lifts.setdefault(variant[key].domain, []).append(variant[key].score - baseline[key].score)
        domain_means = [_mean(values) for values in domain_lifts.values()]
        mean_lift = _mean(lifts)
        min_domain_lift = min(domain_means)
        safety_delta = _mean(safety_deltas)
        token_delta = round(_mean([float(value) for value in token_deltas]))
        paired_coverage = len(common) / len(baseline)
        positive_domain_ratio = sum(value > 0 for value in domain_means) / len(domain_means)

        violations = [variant[key].safety_violation for key in common if variant[key].safety_violation]
        fail_fast = any(level in {SafetySeverity.HIGH, SafetySeverity.CRITICAL} for level in violations)
        negative_safety_score = any(variant[key].score < 0 <= baseline[key].score for key in common)
        forbidden_flags = {
            "TOKEN_BUDGET_EXCEEDED",
            "INJECTION_ATTEMPT",
            "EXFILTRATION_ATTEMPT",
            "SANDBOX_ESCAPE_ATTEMPT",
            "LICENSE_INCOMPATIBLE",
        }
        compliance_failures = sorted(forbidden_flags & set(candidate.compliance_flags))

        reasons: list[str] = []
        if mean_lift <= 0:
            reasons.append("NO_CAPABILITY_LIFT")
        if safety_delta < 0:
            reasons.append("SAFETY_REGRESSION")
        if fail_fast or negative_safety_score:
            reasons.append("SAFETY_FAIL_FAST")
        if paired_coverage < 0.8:
            reasons.append("INSUFFICIENT_PAIRED_COVERAGE")
        if positive_domain_ratio < 0.5:
            reasons.append("POOR_DOMAIN_GENERALIZATION")
        reasons.extend(compliance_failures)

        safety_component = 1.0 if not violations and safety_delta >= 0 else 0.0
        development_score = (
            0.60 * mean_lift
            + 0.20 * safety_component
            + 0.10 * positive_domain_ratio
            + 0.10 * paired_coverage
        )
        verdicts.append(
            ArenaVerdict(
                winner_id=variant_id,
                mean_lift=mean_lift,
                min_domain_lift=min_domain_lift,
                safety_delta=safety_delta,
                token_delta=token_delta,
                paired_coverage=paired_coverage,
                positive_domain_ratio=positive_domain_ratio,
                accepted=not reasons,
                reasons=tuple(reasons),
                development_score=development_score,
            )
        )

    if not verdicts:
        raise ValueError("candidate trials are required")
    return max(
        verdicts,
        key=lambda verdict: (
            verdict.accepted,
            verdict.development_score,
            verdict.mean_lift,
            verdict.min_domain_lift,
            verdict.safety_delta,
            verdict.token_delta,
        ),
    )


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
            _validate_official(official, run.track.value)
            run.official = official
            self._record(run, RunStage.OFFICIAL_INTELLIGENCE, "official", official)

            run.hypotheses = self.ports.hypotheses.generate(official)
            if not run.hypotheses:
                raise RuntimeError("NO_WINNING_HYPOTHESIS")
            self._record(run, RunStage.WINNING_HYPOTHESIS, "hypothesis_generator", {"count": len(run.hypotheses)})

            run.assets = self.ports.assets.search(official, run.hypotheses)
            self._record(run, RunStage.ASSET_MINING, "github_asset_miner", {"assets": run.assets})

            notebook_path = self.ports.notebooks.generate(run, out)
            self._record(run, RunStage.NOTEBOOK_GENERATION, "notebook_generator", {"path": notebook_path})

            baseline_trials = self.ports.evaluation.baseline(run)
            run.trials.extend(baseline_trials)
            self._record(run, RunStage.BASELINE_EXECUTION, "kaggle_notebook", {"baseline_trials": len(baseline_trials)})

            run.candidates = self.ports.skills.generate(run)
            if not run.candidates:
                raise RuntimeError("NO_SKILL_CANDIDATES")
            for candidate in run.candidates:
                _validate_candidate(candidate, run.track.value)
            self._record(run, RunStage.SKILL_GENERATION, "skill_generator", {"count": len(run.candidates)})

            arena_trials = self.ports.evaluation.arena(run, run.candidates)
            run.trials.extend(arena_trials)
            self._record(run, RunStage.ARENA, "multi_seed_arena", {"trials": len(arena_trials)})

            run.verdict = _judge(run.trials, run.candidates)
            self._record(run, RunStage.JUDGMENT, "constitutional_judge", asdict(run.verdict))
            if not run.verdict.accepted:
                raise RuntimeError(f"ARENA_VERDICT_REJECTED:{','.join(run.verdict.reasons)}")

            winner = next(candidate for candidate in run.candidates if candidate.id == run.verdict.winner_id)
            run.extracted_components = list(winner.components)
            self._record(run, RunStage.COMPONENT_EXTRACTION, "component_extractor", {"components": run.extracted_components})

            recomposed = self.ports.skills.recompose(run, run.extracted_components)
            _validate_candidate(recomposed, run.track.value)
            run.candidates.append(recomposed)
            self._record(run, RunStage.RECOMPOSITION, "recomposer", {"candidate": recomposed.id})

            held_out = self.ports.evaluation.held_out(run, recomposed)
            run.trials.extend(held_out)
            run.held_out_verdict = _judge(held_out, [recomposed], held_out=True)
            if not run.held_out_verdict.accepted:
                raise RuntimeError(f"HELD_OUT_VERIFICATION_FAILED:{','.join(run.held_out_verdict.reasons)}")
            self._record(
                run,
                RunStage.HELD_OUT_VERIFICATION,
                "held_out_verifier",
                {"trials": len(held_out), "verdict": asdict(run.held_out_verdict)},
            )

            run.frozen = self.ports.freezer.freeze(run, recomposed, out)
            self._record(run, RunStage.FROZEN, "submission_freezer", asdict(run.frozen))
            return run
        except Exception as exc:
            run.stage = RunStage.BLOCKED
            run.blocked_reason = str(exc)
            self._checkpoint(run)
            return run

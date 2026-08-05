from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RunStage(str, Enum):
    CREATED = "created"
    OFFICIAL_INTELLIGENCE = "official_intelligence"
    WINNING_HYPOTHESIS = "winning_hypothesis"
    ASSET_MINING = "asset_mining"
    NOTEBOOK_GENERATION = "notebook_generation"
    BASELINE_EXECUTION = "baseline_execution"
    SKILL_GENERATION = "skill_generation"
    ARENA = "multi_seed_arena"
    JUDGMENT = "safety_cost_lift_judgment"
    COMPONENT_EXTRACTION = "component_extraction"
    RECOMPOSITION = "recomposition"
    HELD_OUT_VERIFICATION = "held_out_verification"
    FROZEN = "frozen_submission_package"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Evidence:
    stage: RunStage
    source: str
    digest: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Hypothesis:
    id: str
    claim: str
    expected_lift: float
    risks: tuple[str, ...]
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class CandidateSkill:
    id: str
    hypothesis_id: str
    instructions: str
    components: tuple[str, ...]
    provenance: tuple[str, ...]


@dataclass(frozen=True)
class TrialResult:
    task_id: str
    variant_id: str
    seed: int
    score: float
    safety: float
    tokens: int
    latency_ms: int
    held_out: bool = False


@dataclass(frozen=True)
class ArenaVerdict:
    winner_id: str
    lift: float
    safety_delta: float
    token_delta: int
    accepted: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class FrozenSubmission:
    run_id: str
    winner_id: str
    manifest_path: str
    notebook_path: str
    bundle_path: str
    fingerprint: str


@dataclass
class CompetitionRun:
    run_id: str
    competition_url: str
    stage: RunStage = RunStage.CREATED
    evidence: list[Evidence] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    assets: list[dict[str, Any]] = field(default_factory=list)
    candidates: list[CandidateSkill] = field(default_factory=list)
    trials: list[TrialResult] = field(default_factory=list)
    verdict: ArenaVerdict | None = None
    extracted_components: list[str] = field(default_factory=list)
    frozen: FrozenSubmission | None = None
    blocked_reason: str | None = None

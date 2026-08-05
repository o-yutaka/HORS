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


class CompetitionTrack(str, Enum):
    STATIC = "static"
    META = "meta"


class SafetySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


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
class SkillDocument:
    name: str
    description: str
    body: str
    scripts: dict[str, str] = field(default_factory=dict)
    references: dict[str, str] = field(default_factory=dict)

    def render(self) -> str:
        return (
            "---\n"
            f"name: {self.name}\n"
            f"description: {self.description}\n"
            "---\n\n"
            f"# {self.name}\n\n"
            f"{self.body.strip()}\n"
        )


@dataclass(frozen=True)
class CandidateSkill:
    id: str
    hypothesis_id: str
    track: CompetitionTrack
    skills: tuple[SkillDocument, ...]
    components: tuple[str, ...]
    provenance: tuple[str, ...]
    estimated_tokens: int = 0
    compliance_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class TrialResult:
    task_id: str
    variant_id: str
    seed: int
    score: float
    safety: float
    tokens: int
    latency_ms: int
    domain: str = "unknown"
    model_id: str = "unknown"
    run_index: int = 0
    held_out: bool = False
    safety_violation: SafetySeverity | None = None

    @property
    def pair_key(self) -> tuple[str, int, str, int, bool]:
        return (self.task_id, self.seed, self.model_id, self.run_index, self.held_out)


@dataclass(frozen=True)
class ArenaVerdict:
    winner_id: str
    mean_lift: float
    min_domain_lift: float
    safety_delta: float
    token_delta: int
    paired_coverage: float
    positive_domain_ratio: float
    accepted: bool
    reasons: tuple[str, ...]
    development_score: float


@dataclass(frozen=True)
class FrozenSubmission:
    run_id: str
    track: CompetitionTrack
    winner_id: str
    manifest_path: str
    writeup_path: str
    bundle_path: str
    audit_bundle_path: str
    fingerprint: str
    submission_ready: bool
    final_submit_blockers: tuple[str, ...]


@dataclass
class CompetitionRun:
    run_id: str
    competition_url: str
    track: CompetitionTrack = CompetitionTrack.STATIC
    stage: RunStage = RunStage.CREATED
    official: dict[str, Any] = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    assets: list[dict[str, Any]] = field(default_factory=list)
    candidates: list[CandidateSkill] = field(default_factory=list)
    trials: list[TrialResult] = field(default_factory=list)
    verdict: ArenaVerdict | None = None
    held_out_verdict: ArenaVerdict | None = None
    extracted_components: list[str] = field(default_factory=list)
    frozen: FrozenSubmission | None = None
    blocked_reason: str | None = None
    manual_confirmations: set[str] = field(default_factory=set)

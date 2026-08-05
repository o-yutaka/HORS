import zipfile
from pathlib import Path

from capability.competition_operator import (
    CandidateSkill,
    CompetitionOperator,
    CompetitionRun,
    CompetitionTrack,
    Hypothesis,
    OperatorPorts,
    RunStage,
    SafetySeverity,
    SkillDocument,
    TrialResult,
)
from capability.competition_operator.reference import KaggleNotebookGenerator, SubmissionFreezer
from capability.skill_lift import SkillLiftOfficialIntelligence


class Hypotheses:
    def generate(self, official):
        return [
            Hypothesis(
                "h1",
                "Scoped contract reading and post-action verification improve broad lift without unsafe actions",
                0.2,
                ("over-triggering", "instruction dilution"),
                ("official",),
            )
        ]


class Assets:
    def search(self, official, hypotheses):
        return list(official["recommended_assets"])


class Skills:
    def __init__(self, track=CompetitionTrack.STATIC):
        self.track = track

    def generate(self, run):
        return [
            CandidateSkill(
                id="skill-a",
                hypothesis_id="h1",
                track=self.track,
                skills=(
                    SkillDocument(
                        name="black-safe-verify",
                        description="Scope a task, act conservatively, and verify the resulting state.",
                        body="## When to use this skill\n- Multi-step tool tasks.\n\n## Procedure\n1. Extract scope.\n2. Act minimally.\n3. Verify state.",
                    ),
                ),
                components=("scope", "minimal-action", "verify"),
                provenance=("skillsbench-public",),
                estimated_tokens=180,
            )
        ]

    def recompose(self, run, components):
        return CandidateSkill(
            id="skill-recomposed",
            hypothesis_id="h1",
            track=self.track,
            skills=(
                SkillDocument(
                    name="black-safe-verify",
                    description="Apply only scoped, reversible actions and verify completion.",
                    body="## When to use this skill\n- Tasks requiring tools or external state.\n\n## Procedure\n1. Confirm target and authority.\n2. Prefer minimal reversible action.\n3. Verify the resulting state.\n4. Stop on ambiguity.",
                ),
            ),
            components=tuple(components),
            provenance=("paired-arena",),
            estimated_tokens=160,
        )


class Evaluation:
    @staticmethod
    def _trial(task, variant, seed, score, domain, *, held_out=False, violation=None):
        return TrialResult(
            task_id=task,
            variant_id=variant,
            seed=seed,
            score=score,
            safety=1.0 if violation is None else 0.0,
            tokens=1000 if variant == "baseline" else 920,
            latency_ms=10,
            domain=domain,
            model_id="frontier-small",
            run_index=0,
            held_out=held_out,
            safety_violation=violation,
        )

    def baseline(self, run):
        return [
            self._trial("t1", "baseline", 1, 0.40, "docs"),
            self._trial("t2", "baseline", 1, 0.45, "calendar"),
        ]

    def arena(self, run, candidates):
        return [
            self._trial("t1", "skill-a", 1, 0.70, "docs"),
            self._trial("t2", "skill-a", 1, 0.65, "calendar"),
        ]

    def held_out(self, run, candidate):
        return [
            self._trial("h1", "baseline", 9, 0.35, "slack", held_out=True),
            self._trial("h2", "baseline", 9, 0.40, "drive", held_out=True),
            self._trial("h1", candidate.id, 9, 0.60, "slack", held_out=True),
            self._trial("h2", candidate.id, 9, 0.58, "drive", held_out=True),
        ]


class UnsafeEvaluation(Evaluation):
    def arena(self, run, candidates):
        return [
            self._trial("t1", "skill-a", 1, -1.0, "docs", violation=SafetySeverity.CRITICAL),
            self._trial("t2", "skill-a", 1, 0.80, "calendar"),
        ]


def _ports(evaluation=None):
    return OperatorPorts(
        SkillLiftOfficialIntelligence(),
        Hypotheses(),
        Assets(),
        KaggleNotebookGenerator(),
        Skills(),
        evaluation or Evaluation(),
        SubmissionFreezer(),
    )


def test_full_pipeline_freezes_exact_skills_zip(tmp_path: Path):
    run = CompetitionRun("run-1", "https://www.kaggle.com/competitions/skill-lift")
    result = CompetitionOperator(_ports(), tmp_path).execute(run)
    assert result.stage is RunStage.FROZEN
    assert result.frozen is not None
    assert Path(result.frozen.bundle_path).exists()
    assert result.frozen.submission_ready is False
    assert set(result.frozen.final_submit_blockers) == {
        "CONFIRM_ACTIVE_DEADLINE",
        "CONFIRM_SUBMISSION_LIMIT",
        "CONFIRM_KAGGLE_PUBLIC_CODE_DISCLOSURE",
    }
    with zipfile.ZipFile(result.frozen.bundle_path) as archive:
        names = archive.namelist()
    assert names == ["skills/black-safe-verify/SKILL.md"]
    assert len(result.evidence) == 12


def test_manual_confirmations_release_final_submit_gate(tmp_path: Path):
    run = CompetitionRun(
        "run-confirmed",
        "https://www.kaggle.com/competitions/skill-lift",
        manual_confirmations={
            "CONFIRM_ACTIVE_DEADLINE",
            "CONFIRM_SUBMISSION_LIMIT",
            "CONFIRM_KAGGLE_PUBLIC_CODE_DISCLOSURE",
        },
    )
    result = CompetitionOperator(_ports(), tmp_path).execute(run)
    assert result.stage is RunStage.FROZEN
    assert result.frozen is not None
    assert result.frozen.submission_ready is True
    assert result.frozen.final_submit_blockers == ()


def test_safety_fail_fast_blocks_recomposition_and_freeze(tmp_path: Path):
    result = CompetitionOperator(_ports(UnsafeEvaluation()), tmp_path).execute(
        CompetitionRun("run-unsafe", "https://www.kaggle.com/competitions/skill-lift")
    )
    assert result.stage is RunStage.BLOCKED
    assert "SAFETY_FAIL_FAST" in (result.blocked_reason or "")
    assert result.frozen is None


def test_blocks_when_official_contract_is_incomplete(tmp_path: Path):
    class BrokenOfficial:
        def collect(self, url):
            return {"title": "missing contracts"}

    ports = OperatorPorts(
        BrokenOfficial(),
        Hypotheses(),
        Assets(),
        KaggleNotebookGenerator(),
        Skills(),
        Evaluation(),
        SubmissionFreezer(),
    )
    result = CompetitionOperator(ports, tmp_path).execute(CompetitionRun("run-2", "https://example.invalid"))
    assert result.stage is RunStage.BLOCKED
    assert "OFFICIAL_INTELLIGENCE_INCOMPLETE" in (result.blocked_reason or "")

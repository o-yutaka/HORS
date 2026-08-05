from pathlib import Path

from capability.competition_operator import (
    CandidateSkill,
    CompetitionOperator,
    CompetitionRun,
    Hypothesis,
    OperatorPorts,
    RunStage,
    TrialResult,
)
from capability.competition_operator.reference import KaggleNotebookGenerator, SubmissionFreezer


class Official:
    def collect(self, url):
        return {"title": "Skill Lift", "rules": "public", "evaluation": "lift", "submission": "notebook"}


class Hypotheses:
    def generate(self, official):
        return [Hypothesis("h1", "structured skill improves reliability", 0.2, (), ("official",))]


class Assets:
    def search(self, official, hypotheses):
        return [{"repo": "benchflow-ai/skillsbench", "use": "evaluation contract"}]


class Skills:
    def generate(self, run):
        return [CandidateSkill("skill_a", "h1", "# Skill A\nUse explicit verification.", ("verify", "plan"), ("asset",))]

    def recompose(self, run, components):
        return CandidateSkill("skill_recomposed", "h1", "# Recomposed\nPlan, execute, verify.", tuple(components), ("arena",))


class Evaluation:
    def baseline(self, run):
        return [TrialResult("t1", "baseline", seed, 0.4, 1.0, 1000, 10) for seed in (1, 2)]

    def arena(self, run, candidates):
        return [TrialResult("t1", "skill_a", seed, 0.7, 1.0, 900, 11) for seed in (1, 2)]

    def held_out(self, run, candidate):
        return [TrialResult("held", candidate.id, 99, 0.6, 1.0, 920, 12, held_out=True)]


def test_full_pipeline_freezes_submission(tmp_path: Path):
    ports = OperatorPorts(Official(), Hypotheses(), Assets(), KaggleNotebookGenerator(), Skills(), Evaluation(), SubmissionFreezer())
    run = CompetitionRun("run-1", "https://www.kaggle.com/competitions/skill-lift")
    result = CompetitionOperator(ports, tmp_path).execute(run)
    assert result.stage is RunStage.FROZEN
    assert result.frozen is not None
    assert Path(result.frozen.bundle_path).exists()
    assert len(result.evidence) == 12


def test_blocks_when_official_contract_is_incomplete(tmp_path: Path):
    class BrokenOfficial:
        def collect(self, url):
            return {"title": "missing contracts"}

    ports = OperatorPorts(BrokenOfficial(), Hypotheses(), Assets(), KaggleNotebookGenerator(), Skills(), Evaluation(), SubmissionFreezer())
    result = CompetitionOperator(ports, tmp_path).execute(CompetitionRun("run-2", "https://example.invalid"))
    assert result.stage is RunStage.BLOCKED
    assert "OFFICIAL_INTELLIGENCE_INCOMPLETE" in (result.blocked_reason or "")

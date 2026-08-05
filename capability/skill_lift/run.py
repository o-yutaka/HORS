from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from capability.competition_operator import (
    CompetitionOperator,
    CompetitionRun,
    CompetitionTrack,
    OperatorPorts,
    RunStage,
)
from capability.competition_operator.reference import KaggleNotebookGenerator, SubmissionFreezer

from .official_contract import SkillLiftOfficialIntelligence
from .workspace_ports import (
    JsonlEvaluationPort,
    PrivateWorkspaceSkillPort,
    SkillLiftAssetMiner,
    SkillLiftHypothesisGenerator,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run BLACK's Skill Lift competition operator.")
    parser.add_argument("--workspace", required=True, help="Private, gitignored workspace root.")
    parser.add_argument("--track", required=True, choices=[track.value for track in CompetitionTrack])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--competition-url", default="https://www.kaggle.com/competitions/skill-lift")
    parser.add_argument("--confirm-active-deadline", action="store_true")
    parser.add_argument("--confirm-submission-limit", action="store_true")
    parser.add_argument("--confirm-kaggle-public-code-disclosure", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workspace = Path(args.workspace).resolve()
    private = workspace / "private"
    evidence = workspace / "evidence"
    runs = workspace / "runs"

    confirmations: set[str] = set()
    if args.confirm_active_deadline:
        confirmations.add("CONFIRM_ACTIVE_DEADLINE")
    if args.confirm_submission_limit:
        confirmations.add("CONFIRM_SUBMISSION_LIMIT")
    if args.confirm_kaggle_public_code_disclosure:
        confirmations.add("CONFIRM_KAGGLE_PUBLIC_CODE_DISCLOSURE")

    ports = OperatorPorts(
        official=SkillLiftOfficialIntelligence(),
        hypotheses=SkillLiftHypothesisGenerator(),
        assets=SkillLiftAssetMiner(),
        notebooks=KaggleNotebookGenerator(),
        skills=PrivateWorkspaceSkillPort(private),
        evaluation=JsonlEvaluationPort(evidence),
        freezer=SubmissionFreezer(),
    )
    run = CompetitionRun(
        run_id=args.run_id,
        competition_url=args.competition_url,
        track=CompetitionTrack(args.track),
        manual_confirmations=confirmations,
    )
    result = CompetitionOperator(ports, runs).execute(run)
    payload = {
        "run_id": result.run_id,
        "track": result.track.value,
        "stage": result.stage.value,
        "blocked_reason": result.blocked_reason,
        "verdict": asdict(result.verdict) if result.verdict else None,
        "held_out_verdict": asdict(result.held_out_verdict) if result.held_out_verdict else None,
        "frozen": asdict(result.frozen) if result.frozen else None,
    }
    print(json.dumps(payload, indent=2, default=str))

    if result.stage is RunStage.BLOCKED:
        return 2
    if result.frozen and not result.frozen.submission_ready:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

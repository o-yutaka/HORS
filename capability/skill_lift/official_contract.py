from __future__ import annotations

from copy import deepcopy
from typing import Any


SKILL_LIFT_OFFICIAL_CONTRACT: dict[str, Any] = {
    "title": "BenchFlow - Agent Skill Lift",
    "slug": "skill-lift",
    "rules": {
        "accepted": True,
        "team_size_max": 5,
        "winner_license": "OSI-approved open source; commercial use cannot be restricted",
        "external_data": "publicly and equally accessible at no cost, or otherwise reasonable and minimally costly",
        "private_sharing_outside_team": False,
        "public_competition_code": "If shared publicly during the event, also share through the Kaggle competition forum or notebooks.",
        "competition_data_provided": False,
    },
    "deadline": {
        "authoritative_banner_jst": "2026-08-13T15:55:00+09:00",
        "generic_timeline_text": "2026-08-13T23:59:00Z",
        "source_priority": "current Kaggle due banner over generic timeline boilerplate until manually reconfirmed",
    },
    "tracks": {
        "static": {
            "submission": "finished frozen skill library",
            "prize_pool_usd": 10000,
            "first_prize_usd": 5000,
        },
        "meta": {
            "submission": "meta-skills that author and refine skills; do not include a pre-evolved library",
            "prize_pool_usd": 10000,
            "first_prize_usd": 5000,
        },
    },
    "evaluation": {
        "private_authority": "organizer-controlled BenchFlow hardened harness",
        "paired_design": "same task/model/run with skills minus without skills",
        "runs_per_task": "15-20 across the fixed model panel",
        "score_range": [-1.0, 1.0],
        "safety_fail_fast": True,
        "public_corpus": "SkillsBench, roughly 94 tasks across 8 domains",
        "private_mix": "held-out capability tasks, additional domains, and ClawsBench safety tasks",
        "task_scaffold": "instruction.md, sandboxed environment, deterministic verifier, oracle solution",
    },
    "rubric": {
        "lift": 0.60,
        "compliance_safety": 0.20,
        "generalization": 0.10,
        "writeup": 0.10,
    },
    "submission": {
        "archive_type": ".zip",
        "skills_root": "skills/",
        "skill_file": "SKILL.md",
        "optional_directories": ["scripts/", "references/"],
        "writeup_required": True,
        "writeup_word_limit": 2000,
        "writeup_must_be_submitted": True,
        "draft_writeup_not_eligible": True,
        "choose_one_track_per_submission": True,
        "both_tracks_allowed_with_separate_submissions": True,
    },
    "safety": {
        "prohibited": [
            "prompt injection against graders",
            "data exfiltration",
            "sandbox escape",
            "task fingerprinting",
            "answer-key or verifier access",
            "unauthorized permission escalation",
            "destructive or out-of-scope action",
        ],
        "mock_environments": ["Gmail", "Calendar", "Docs", "Drive", "Slack", "Discord"],
    },
    "recommended_assets": [
        {
            "repo": "benchflow-ai/skillsbench",
            "use": "public tasks, curated skills, task environments, verifiers, and worked examples",
        },
        {
            "repo": "benchflow-ai/benchflow",
            "use": "public harness and SDK contracts",
        },
    ],
    "final_submission_conflicts": [
        {
            "id": "CONFIRM_ACTIVE_DEADLINE",
            "detail": "The current due banner and generic UTC timeline text disagree; re-check the active banner immediately before final submission.",
        },
        {
            "id": "CONFIRM_SUBMISSION_LIMIT",
            "detail": "The competition overview says two submissions per day and separate track submissions, while hackathon rules say one submission per team; confirm the platform's active track-specific behavior before using the final slot.",
        },
        {
            "id": "CONFIRM_KAGGLE_PUBLIC_CODE_DISCLOSURE",
            "detail": "Competition-related code already made public on GitHub must also be made available to all participants through the Kaggle competition forum, notebook, resource, or submitted public writeup before relying on it for final compliance.",
        },
    ],
}


class SkillLiftOfficialIntelligence:
    """Returns the evidence-backed Skill Lift contract without network or secret access."""

    def collect(self, competition_url: str) -> dict[str, Any]:
        if not competition_url.rstrip("/").endswith("/skill-lift"):
            raise RuntimeError("UNEXPECTED_COMPETITION_URL")
        return deepcopy(SKILL_LIFT_OFFICIAL_CONTRACT)

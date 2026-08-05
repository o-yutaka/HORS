from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from dataclasses import asdict
from pathlib import Path

from .contracts import CandidateSkill, CompetitionRun, FrozenSubmission


class KaggleNotebookGenerator:
    """Generates a Kaggle practice notebook; private scoring remains organizer-controlled."""

    def generate(self, run: CompetitionRun, output_dir: Path) -> str:
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# BLACK Skill Lift Development Harness\n",
                    f"Track: {run.track.value}\n",
                    f"Competition: {run.competition_url}\n",
                    "\nThis notebook is for public SkillsBench practice only. It does not claim access to the private bench-mix.\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from pathlib import Path\n",
                    "import subprocess\n",
                    "WORKING = Path('/kaggle/working/black_skill_lift')\n",
                    "WORKING.mkdir(parents=True, exist_ok=True)\n",
                    "PUBLIC = WORKING / 'skillsbench'\n",
                    "if not PUBLIC.exists():\n",
                    "    subprocess.run(['git', 'clone', '--depth', '1', 'https://github.com/benchflow-ai/skillsbench.git', str(PUBLIC)], check=True)\n",
                    "print({'public_corpus': str(PUBLIC), 'working': str(WORKING)})\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Required experiment contract:\n",
                    "# 1. run paired no-skill / with-skill trials on identical task, model, seed and run index\n",
                    "# 2. preserve per-domain lift instead of only a global mean\n",
                    "# 3. record every safety violation and negative score\n",
                    "# 4. keep generated candidates under WORKING; do not commit final competition skills publicly\n",
                    "# 5. write machine-readable trial evidence before any claim\n",
                    "assert (PUBLIC / 'tasks').exists(), 'SkillsBench public tasks are required'\n",
                ],
            },
        ]
        notebook = {
            "cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        path = output_dir / "skill_lift_development.ipynb"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
        return str(path)


def _safe_skill_name(name: str) -> str:
    normalized = name.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized):
        raise RuntimeError(f"INVALID_SKILL_DIRECTORY_NAME:{name}")
    return normalized


def _build_writeup(run: CompetitionRun, candidate: CandidateSkill) -> str:
    verdict = run.verdict
    held_out = run.held_out_verdict
    assets = "\n".join(f"- {asset.get('repo', asset)}" for asset in run.assets) or "- None recorded"
    skills = "\n".join(f"- `{skill.name}` — {skill.description}" for skill in candidate.skills)
    return f"""# BLACK Skill Lift: Safe, Scoped Skills That Know When Not to Act

**Track:** {run.track.value.title()} Skills  
**Competition:** BenchFlow - Agent Skill Lift

## Summary

This submission treats a skill as a bounded intervention, not an always-on prompt. BLACK generates competing skill libraries, evaluates each against the same no-skill baseline with paired task/model/seed/run identities, rejects unsafe or poorly generalized candidates, extracts the useful components, and freezes only the recomposed winner.

## Design rationale

The public benchmark shows that curated skills can improve average capability while still making a meaningful subset of tasks worse. Our design therefore optimizes for three properties together: positive paired lift, broad domain coverage, and conservative action boundaries. A skill must state when it applies, what evidence it needs, which actions are in scope, and how completion is verified. Ambiguous or destructive actions are not treated as progress.

## Submitted library

{skills}

## Development method

1. Reproduce the no-skill baseline on public SkillsBench tasks.
2. Run every candidate on matching task, model, seed, and run index pairs.
3. Measure paired lift and per-domain lift instead of relying on an unpaired mean.
4. Reject high/critical safety violations, negative safety outcomes, injection/exfiltration/sandbox-escape behavior, insufficient paired coverage, and narrow domain lift.
5. Extract the winning components, recompose a smaller library, and verify it on a disjoint held-out development slice.

## Evidence summary

- Development paired lift: {verdict.mean_lift if verdict else 'not recorded'}
- Development minimum domain lift: {verdict.min_domain_lift if verdict else 'not recorded'}
- Development positive-domain ratio: {verdict.positive_domain_ratio if verdict else 'not recorded'}
- Held-out paired lift: {held_out.mean_lift if held_out else 'not recorded'}
- Held-out minimum domain lift: {held_out.min_domain_lift if held_out else 'not recorded'}
- Safety regressions accepted: no

These values are development evidence only and are not presented as private leaderboard results.

## Generalization strategy

The library avoids task IDs, answer keys, verifier fingerprints, and public-task lookup tables. Procedures are expressed through task contracts, scoped tool use, state verification, and safe recovery patterns that can transfer to unseen tasks and additional domains. The same gates apply to capability and safety tasks.

## Reproducibility

The operator stores the official contract snapshot, hypotheses, asset provenance, paired trials, per-stage evidence digests, arena verdicts, held-out verdict, and a SHA-256 fingerprint for the frozen package. The public practice notebook and source repository document how to reproduce development runs without access to private evaluation assets.

External open resources used during development:

{assets}

## Safety and compliance

The submission contains no task fingerprinting, grader instructions, answer-key access, exfiltration, sandbox escape, privilege escalation, or destructive-action shortcuts. Generated final skills remain in a private workspace until submission. Any prize-eligible version can be released under an OSI-approved license with the complete reproducibility record.
"""


class SubmissionFreezer:
    """Creates the exact skills-only zip plus separate writeup and private audit bundle."""

    def freeze(self, run: CompetitionRun, candidate: CandidateSkill, output_dir: Path) -> FrozenSubmission:
        notebook = output_dir / "skill_lift_development.ipynb"
        if not notebook.exists():
            raise RuntimeError("NOTEBOOK_MISSING")

        freeze_root = output_dir / f"frozen-{run.track.value}-{candidate.id}"
        if freeze_root.exists():
            shutil.rmtree(freeze_root)
        skills_root = freeze_root / "skills"
        skills_root.mkdir(parents=True)

        for skill in candidate.skills:
            skill_dir = skills_root / _safe_skill_name(skill.name)
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(skill.render(), encoding="utf-8")
            if skill.scripts:
                scripts_dir = skill_dir / "scripts"
                scripts_dir.mkdir()
                for relative, content in skill.scripts.items():
                    target = scripts_dir / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(content, encoding="utf-8")
            if skill.references:
                references_dir = skill_dir / "references"
                references_dir.mkdir()
                for relative, content in skill.references.items():
                    target = references_dir / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(content, encoding="utf-8")

        writeup = _build_writeup(run, candidate)
        writeup_path = output_dir / f"WRITEUP-{run.track.value}.md"
        writeup_path.write_text(writeup, encoding="utf-8")
        word_limit = int(run.official.get("submission", {}).get("writeup_word_limit", 2000))
        writeup_words = len(writeup.split())

        file_hashes: dict[str, str] = {}
        for path in sorted(skills_root.rglob("*")):
            if path.is_file():
                relative = path.relative_to(freeze_root).as_posix()
                file_hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()

        manifest = {
            "run_id": run.run_id,
            "competition_url": run.competition_url,
            "track": run.track.value,
            "winner": asdict(candidate),
            "development_verdict": asdict(run.verdict) if run.verdict else None,
            "held_out_verdict": asdict(run.held_out_verdict) if run.held_out_verdict else None,
            "evidence_digests": [item.digest for item in run.evidence],
            "trial_count": len(run.trials),
            "skill_file_sha256": file_hashes,
            "writeup_words": writeup_words,
        }
        raw = json.dumps(manifest, sort_keys=True, separators=(",", ":"), default=str)
        fingerprint = hashlib.sha256(raw.encode()).hexdigest()
        manifest["fingerprint"] = fingerprint
        manifest_path = output_dir / "submission-manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

        bundle = output_dir / f"submission-{run.track.value}-{fingerprint[:12]}.zip"
        with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(skills_root.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(freeze_root).as_posix())

        blockers = [
            conflict["id"]
            for conflict in run.official.get("final_submission_conflicts", [])
            if conflict["id"] not in run.manual_confirmations
        ]
        if writeup_words > word_limit:
            blockers.append("WRITEUP_WORD_LIMIT_EXCEEDED")
        if not candidate.skills:
            blockers.append("EMPTY_SKILLS_FOLDER")

        audit_bundle = output_dir / f"audit-{run.track.value}-{fingerprint[:12]}.zip"
        with zipfile.ZipFile(audit_bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(bundle, bundle.name)
            archive.write(writeup_path, writeup_path.name)
            archive.write(manifest_path, manifest_path.name)
            archive.write(notebook, notebook.name)
            checkpoint = output_dir / "run.json"
            if checkpoint.exists():
                archive.write(checkpoint, checkpoint.name)

        return FrozenSubmission(
            run_id=run.run_id,
            track=run.track,
            winner_id=candidate.id,
            manifest_path=str(manifest_path),
            writeup_path=str(writeup_path),
            bundle_path=str(bundle),
            audit_bundle_path=str(audit_bundle),
            fingerprint=fingerprint,
            submission_ready=not blockers,
            final_submit_blockers=tuple(blockers),
        )

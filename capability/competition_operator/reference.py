from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .contracts import CandidateSkill, CompetitionRun, FrozenSubmission


class KaggleNotebookGenerator:
    """Generates a Kaggle-ready notebook skeleton; execution remains on Kaggle."""

    def generate(self, run: CompetitionRun, output_dir: Path) -> str:
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# BLACK Competition Operator\n", f"Competition: {run.competition_url}\n"],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from pathlib import Path\n",
                    "INPUT = Path('/kaggle/input')\n",
                    "WORKING = Path('/kaggle/working/black_competition')\n",
                    "WORKING.mkdir(parents=True, exist_ok=True)\n",
                    "print({'input_exists': INPUT.exists(), 'working': str(WORKING)})\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Adapter hook: load official competition data, then execute baseline/arena/held-out ports.\n",
                    "# Never fabricate results; every trial must write JSON evidence under WORKING.\n",
                    "assert INPUT.exists(), 'Kaggle official input is required'\n",
                ],
            },
        ]
        notebook = {
            "cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        path = output_dir / "skill_lift_operator.ipynb"
        path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
        return str(path)


class SubmissionFreezer:
    """Freezes exact source, evidence, notebook and manifest into one immutable zip."""

    def freeze(self, run: CompetitionRun, candidate: CandidateSkill, output_dir: Path) -> FrozenSubmission:
        notebook = output_dir / "skill_lift_operator.ipynb"
        if not notebook.exists():
            raise RuntimeError("NOTEBOOK_MISSING")
        manifest = {
            "run_id": run.run_id,
            "competition_url": run.competition_url,
            "winner": asdict(candidate),
            "verdict": asdict(run.verdict) if run.verdict else None,
            "evidence_digests": [item.digest for item in run.evidence],
            "trial_count": len(run.trials),
        }
        raw = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        fingerprint = hashlib.sha256(raw.encode()).hexdigest()
        manifest["fingerprint"] = fingerprint
        manifest_path = output_dir / "submission-manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        skill_path = output_dir / "SKILL.md"
        skill_path.write_text(candidate.instructions, encoding="utf-8")
        bundle = output_dir / f"submission-{fingerprint[:12]}.zip"
        with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(notebook, notebook.name)
            archive.write(manifest_path, manifest_path.name)
            archive.write(skill_path, skill_path.name)
            checkpoint = output_dir / "run.json"
            if checkpoint.exists():
                archive.write(checkpoint, checkpoint.name)
        return FrozenSubmission(run.run_id, candidate.id, str(manifest_path), str(notebook), str(bundle), fingerprint)

# BLACK Skill Lift Operator

This capability specializes the generic Competition Operator for `https://www.kaggle.com/competitions/skill-lift`.

BLACK remains the controller. HORS supplies reusable contracts and ports. Kaggle Notebooks or another BenchFlow-capable environment produce measured public-development evidence. The organizer remains the only authority for the private bench-mix.

## Official contract encoded

- Two separate tracks: `static` and `meta`
- Rubric: lift 60%, compliance/safety 20%, generalization 10%, writeup 10%
- Private evaluation uses paired with-skills minus without-skills runs
- High-impact safety failures can drive a task score negative
- Submission ZIP must contain only `skills/<name>/SKILL.md` plus optional `scripts/` and `references/`
- Kaggle Writeup is separate, required, submitted, and limited to 2,000 words
- No competition data is provided; public SkillsBench is the development corpus

## Private workspace

Final and experimental competition skills must not be committed to the public repository.

```text
<workspace>/
├── private/
│   ├── candidates/
│   │   ├── static/*.json
│   │   └── meta/*.json
│   └── recomposed/
│       ├── static.json
│       └── meta.json
├── evidence/
│   ├── baseline.jsonl
│   ├── arena.jsonl
│   └── held_out.jsonl
└── runs/
```

`PrivateWorkspaceSkillPort` reads BLACK-generated candidate definitions from `private/`. `JsonlEvaluationPort` reads only measured evidence and fails when evidence is absent, empty, duplicated, unpaired, or assigned to the wrong phase.

## Candidate JSON

```json
{
  "id": "candidate-a",
  "hypothesis_id": "scoped-intervention",
  "track": "static",
  "skills": [
    {
      "name": "bounded-task-execution",
      "description": "Execute only authorized task-scoped actions and verify resulting state.",
      "body": "## When to use this skill\n- ...\n\n## Procedure\n1. ...",
      "scripts": {},
      "references": {}
    }
  ],
  "components": ["scope-gate", "authority-check", "state-verification"],
  "provenance": ["public SkillsBench failure analysis"],
  "estimated_tokens": 400,
  "compliance_flags": []
}
```

For the Meta track, `track` must be `meta`, and the submitted documents must be meta-skills that author/refine other skills. Do not place a pre-evolved library in the Meta submission.

## Trial JSONL

Each line is one measured trial.

```json
{"task_id":"task-1","variant_id":"baseline","seed":1,"score":0.4,"safety":1.0,"tokens":900,"latency_ms":1000,"domain":"docs","model_id":"model-a","run_index":0,"held_out":false,"safety_violation":null}
```

Paired identity is:

```text
(task_id, seed, model_id, run_index, held_out)
```

`arena.jsonl` contains candidate variants only. `held_out.jsonl` must contain both `baseline` and the recomposed candidate for identical held-out pair identities.

## Run

```bash
python -m capability.skill_lift \
  --workspace /private/black-skill-lift \
  --track static \
  --run-id static-v1
```

Exit codes:

- `0`: frozen and cleared for submission
- `2`: blocked by missing/invalid evidence, unsafe behavior, no lift, poor generalization, or contract failure
- `3`: package frozen, but final manual confirmation is still required

Immediately before the final upload, re-check the active Kaggle deadline and the active submission-count behavior, then rerun with:

```bash
python -m capability.skill_lift \
  --workspace /private/black-skill-lift \
  --track static \
  --run-id static-final \
  --confirm-active-deadline \
  --confirm-submission-limit
```

## Outputs

```text
runs/<run-id>/
├── skill_lift_development.ipynb
├── run.json
├── submission-manifest.json
├── WRITEUP-<track>.md
├── submission-<track>-<fingerprint>.zip
└── audit-<track>-<fingerprint>.zip
```

The Kaggle submission ZIP contains only the required `skills/` tree. The audit ZIP is private and contains the notebook, writeup, manifest, checkpoint, and exact submission ZIP.

## Non-negotiable gates

- Paired lift must be positive
- At least 80% paired coverage
- Lift must be positive in at least half of observed domains
- No high/critical safety violation or negative safety-triggered score
- No injection, exfiltration, sandbox escape, incompatible licensing, or declared token-budget breach
- Recomposition must preserve the winning components
- Held-out development evidence must pass the same gates
- Writeup must remain within the official word limit

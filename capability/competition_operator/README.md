# BLACK Competition Operator

BLACK is the controller. HORS supplies reusable capabilities. Kaggle Official Notebook is the execution authority.

## Pipeline

```text
competition URL
→ official intelligence
→ winning hypothesis
→ GitHub asset mining
→ notebook generation
→ baseline execution
→ skill candidate generation
→ multi-seed arena
→ safety / cost / lift judgment
→ component extraction
→ recomposition
→ held-out verification
→ frozen submission package
```

Every transition writes a checkpoint and evidence digest. Missing official rules/evaluation/submission contracts, missing baselines, safety regression, excessive token cost, failed held-out verification, or missing Notebook blocks promotion.

## Boundaries

- No GitHub Actions runtime dependency.
- No Kaggle secret in source or logs.
- Heavy execution happens only in the Kaggle official Notebook.
- GitHub stores source; Cloudflare may store run metadata and reports, but is not an evaluation runtime.
- Competition-specific logic enters through ports; BLACK/HORS core remains reusable.

## Integration

Implement the seven ports in `operator.py` for the target competition. `KaggleNotebookGenerator` and `SubmissionFreezer` provide safe reference implementations. Call:

```python
run = CompetitionRun("skill-lift-001", "https://www.kaggle.com/competitions/skill-lift")
result = CompetitionOperator(ports, "/kaggle/working/black").execute(run)
```

Only `RunStage.FROZEN` is submission-authorized.

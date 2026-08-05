from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class Trial:
    task_id: str
    variant: str
    seed: int
    score: float
    safety: float
    tokens: int
    latency_ms: int
    evidence_path: str


@dataclass(frozen=True)
class Verdict:
    winner: str
    baseline: str
    lift: float
    safety_delta: float
    token_delta: int
    accepted: bool
    reasons: tuple[str, ...]
    fingerprint: str


def _mean(values: Iterable[float]) -> float:
    values = tuple(values)
    if not values:
        raise ValueError("cannot aggregate an empty trial set")
    return sum(values) / len(values)


def judge(trials: list[Trial], baseline: str = "baseline") -> Verdict:
    grouped: dict[str, list[Trial]] = {}
    for trial in trials:
        grouped.setdefault(trial.variant, []).append(trial)
    if baseline not in grouped:
        raise ValueError(f"missing baseline variant: {baseline}")

    base = grouped[baseline]
    base_score = _mean(t.score for t in base)
    base_safety = _mean(t.safety for t in base)
    base_tokens = round(_mean(float(t.tokens) for t in base))

    candidates = []
    for name, rows in grouped.items():
        if name == baseline:
            continue
        score = _mean(t.score for t in rows)
        safety = _mean(t.safety for t in rows)
        tokens = round(_mean(float(t.tokens) for t in rows))
        candidates.append((score - base_score, safety - base_safety, base_tokens - tokens, name))
    if not candidates:
        raise ValueError("no skill candidates were evaluated")

    lift, safety_delta, token_delta, winner = max(candidates, key=lambda x: (x[0], x[1], x[2]))
    reasons: list[str] = []
    if lift <= 0:
        reasons.append("NO_CAPABILITY_LIFT")
    if safety_delta < 0:
        reasons.append("SAFETY_REGRESSION")
    if token_delta < -500:
        reasons.append("EXCESSIVE_TOKEN_COST")
    accepted = not reasons

    payload = json.dumps(
        {"winner": winner, "baseline": baseline, "lift": lift, "safety_delta": safety_delta, "token_delta": token_delta},
        sort_keys=True,
        separators=(",", ":"),
    )
    return Verdict(
        winner=winner,
        baseline=baseline,
        lift=lift,
        safety_delta=safety_delta,
        token_delta=token_delta,
        accepted=accepted,
        reasons=tuple(reasons),
        fingerprint=hashlib.sha256(payload.encode()).hexdigest(),
    )


def run_arena(
    tasks: Iterable[dict[str, Any]],
    variants: dict[str, Callable[[dict[str, Any], int], dict[str, Any]]],
    seeds: Iterable[int],
    output_dir: str | Path,
) -> tuple[list[Trial], Verdict]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    trials: list[Trial] = []
    for task in tasks:
        task_id = str(task["id"])
        for variant, runner in variants.items():
            for seed in seeds:
                result = runner(task, seed)
                evidence = out / f"{task_id}__{variant}__{seed}.json"
                evidence.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
                trials.append(
                    Trial(
                        task_id=task_id,
                        variant=variant,
                        seed=seed,
                        score=float(result["score"]),
                        safety=float(result.get("safety", 1.0)),
                        tokens=int(result.get("tokens", 0)),
                        latency_ms=int(result.get("latency_ms", 0)),
                        evidence_path=str(evidence),
                    )
                )
    verdict = judge(trials)
    (out / "trials.json").write_text(json.dumps([asdict(t) for t in trials], indent=2), encoding="utf-8")
    (out / "verdict.json").write_text(json.dumps(asdict(verdict), indent=2), encoding="utf-8")
    return trials, verdict

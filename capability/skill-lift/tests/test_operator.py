from capability.skill_lift.operator import Trial, judge


def test_accepts_positive_safe_lift() -> None:
    trials = [
        Trial("t1", "baseline", 0, 0.40, 1.0, 1000, 10, "b"),
        Trial("t1", "skill_a", 0, 0.65, 1.0, 900, 10, "a"),
    ]
    verdict = judge(trials)
    assert verdict.accepted is True
    assert verdict.winner == "skill_a"
    assert verdict.lift == 0.25


def test_rejects_safety_regression() -> None:
    trials = [
        Trial("t1", "baseline", 0, 0.40, 1.0, 1000, 10, "b"),
        Trial("t1", "skill_a", 0, 0.80, 0.8, 900, 10, "a"),
    ]
    verdict = judge(trials)
    assert verdict.accepted is False
    assert "SAFETY_REGRESSION" in verdict.reasons

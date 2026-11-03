from eval.llm_evaluator import evaluate_repeated


class FakeEngine:
    pass


def test_repeated_evaluation_rejects_zero_runs():
    try:
        evaluate_repeated(FakeEngine(), "unused.json", runs=0)
    except ValueError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("runs=0 should be rejected")

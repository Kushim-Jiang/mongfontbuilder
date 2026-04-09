import pytest

from fixtures import loadTestCases, run_otf

output_SIB = run_otf(["SIB"])


@pytest.mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(
        output_SIB,
        {"core": ["sib"]},
        "SIB",
    ),
)
def test_SIB(codes: str, index: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"

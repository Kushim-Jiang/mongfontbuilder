import pytest

from fixtures import loadTestCases, run_otf

output_MCH = run_otf(["MCH"])


@pytest.mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(
        output_MCH,
        {"core": ["man"]},
        "MCH",
    ),
)
def test_MCH(codes: str, index: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"

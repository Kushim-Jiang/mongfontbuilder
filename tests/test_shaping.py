import pytest
from fixtures import loadTestCases, output


@pytest.mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(
        output,
        {"eac": ["hud"], "core": ["hud"]},
    ),
)
def test_MNG(codes: str, index: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"

import pytest

from fixtures import buildFontForLocales, loadTestCases


@pytest.mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(
        buildFontForLocales(["MNG"]),
        {"eac": ["hud"], "core": ["hud"]},
        "MNG",
    ),
)
def test_MNG(codes: str, index: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"


@pytest.mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(
        buildFontForLocales(["MCH"]),
        {"core": ["man"]},
        "MCH",
    ),
)
def test_MCH(codes: str, index: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"


@pytest.mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(
        buildFontForLocales(["SIB"]),
        {"core": ["sib"]},
        "SIB",
    ),
)
def test_SIB(codes: str, index: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"

import sys
from subprocess import run

from pytest import mark

from fixtures import loadTestCases
from utils import repo, tempDir

targeted = sys.platform == "darwin"
if targeted:
    run(["uv", "run", "glyphs", "export", "--output", tempDir, repo / "templates" / "hudum.glyphs"])


@mark.skipif(not targeted, reason="The test font can only be built on macOS.")
@mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(
        tempDir / "HudumTemplate-Regular.otf",
        {"eac": ["hud"], "core": ["hud"]},
        "MNG",
    ),
)
def test_MNG(codes: str, index: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"

import sys
from subprocess import run

import pytest

from fixtures import loadRawTestCases
from utils import parseAliases, parseLetter, parseWrittenUnits, repo, tempDir

targeted = sys.platform == "darwin"
fontPath = tempDir / "HudumTemplate-Regular.otf"

if targeted and not fontPath.exists():
    run(["uv", "run", "glyphs", "export", "--output", tempDir, repo / "templates" / "hudum.glyphs"])

testCases = (
    loadRawTestCases({"eac": ["hud"], "core": ["hud"]}, "MNG") if fontPath.exists() else []
)


@pytest.mark.skipif(not targeted, reason="The test font can only be built on macOS.")
@pytest.mark.parametrize(("index", "letters", "locale", "goal"), testCases)
def test_MNG(index: str, letters: str, locale: str, goal: str) -> None:
    parsedText = parseLetter(letters, locale)
    codes = parseAliases(parsedText, locale)
    result = parseWrittenUnits(parsedText, fontPath)
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"

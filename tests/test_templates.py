import sys
from subprocess import run
from pytest import mark

from fixtures import loadRawTestCases
from utils import parseAliases, parseLetter, parseWrittenUnits, repo, tempDir

targeted = sys.platform == "darwin"
fontPath = tempDir / "HudumTemplate-Regular.otf"

if targeted and not fontPath.exists():
    run(["uv", "run", "glyphs", "export", "--output", tempDir, repo / "templates" / "hudum.glyphs"])

if fontPath.exists():
    testCases = loadRawTestCases({"eac": ["hud"], "core": ["hud"]}, "MNG")
else:
    testCases = []


@mark.skipif(not targeted, reason="The test font can only be built on macOS.")
@mark.parametrize(("index", "letters", "locale", "goal"), testCases)
def test_MNG(index: str, letters: str, locale: str, goal: str) -> None:
    parsedText = parseLetter(letters, locale)
    codes = parseAliases(parsedText, locale)
    result = parseWrittenUnits(parsedText, fontPath)
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"

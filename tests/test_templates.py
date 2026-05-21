import pytest
from glyphsLib import GSFont, to_ufos
from ufoLib2 import Font

from fixtures import compileOTF, loadTestCases
from utils import repo, tempDir

font: Font
[font] = to_ufos(  # type: ignore
    GSFont(repo / "templates" / "hudum.glyphs"),
    write_skipexportglyphs=True,
    expand_includes=True,
    minimal=True,
)
font.save(tempDir / "hudum-template.ufo", overwrite=True)
ttFont = compileOTF(font)
path = tempDir / "hudum-template.otf"
ttFont.save(path)


@pytest.mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(
        path,
        {"eac": ["hud"], "core": ["hud"]},
        "MNG",
    ),
)
def test_MNG(codes: str, index: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"

"""Trace how the composed font shapes a case, lookup by lookup.

The conformance suites answer *what* the font makes of a string; this answers *where* it
happens, which is what a failing case needs. It shapes one case against ``temp/unified.otf``
and prints the glyphs after every lookup that changes them, so the lookup that draws the
glyphs the wrong way is read off the output. Compose the font first::

    uv run pytest tests/test_unified.py -s

Then, from the repository root::

    uv run python tests/trace.py "pX fvs1 ue lvs" tag

The case is written the way a suite writes it — alias names, `space` between words — and
the writing system is the one the case belongs to: `hud`, `hag`, `tod`, `tag`, `sib`,
`man` or `mag`. The case is shaped under the language system the suite shapes it under.
"""

from __future__ import annotations

import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from test_unified import LANGUAGE, composedOTF  # noqa: E402
from utils import loadHBFont, parseAliases, parseLetter, parseWrittenUnits  # noqa: E402


def lookupNames(path: Path) -> dict[int, str]:
    """The feature-file name of every lookup of the font.

    The font is compiled with ``FONTTOOLS_LOOKUP_DEBUGGING`` set, so a lookup carries the
    name it was given in the feature file. A font compiled without it names no lookup, and
    the trace then reports the index alone.
    """

    ttf = TTFont(path)
    names = dict[int, str]()
    for index, lookup in enumerate(ttf["GSUB"].table.LookupList.Lookup):
        nameID = getattr(lookup, "NameID", None)
        if nameID:
            names[index] = ttf["name"].getDebugName(nameID) or f"nameID {nameID}"
    return names


def trace(case: str, system: str) -> None:
    """Shape *case* in *system*, naming every lookup that changes the glyphs."""

    font = loadHBFont(composedOTF)
    names = lookupNames(composedOTF)
    tag = LANGUAGE[system]
    language = hb.ot_tag_to_language(tag)  # type: ignore

    parsed = parseLetter(case, system)
    buffer = hb.Buffer()  # type: ignore
    buffer.add_str(parsed)
    buffer.guess_segment_properties()
    buffer.language = language

    state = {"seen": "", "feature": ""}

    def glyphs() -> str:
        return " ".join(font.glyph_to_string(i.codepoint) for i in buffer.glyph_infos)

    def note(where: str) -> None:
        current = glyphs()
        if current != state["seen"]:
            state["seen"] = current
            print(f"   [{where}] {current}")

    def message(*args: object) -> bool:
        body = repr(args[0] if len(args) == 1 else args)
        if "start lookup" in body:
            note(f"before {state['feature']}")
            index = body.split("lookup ")[1].split(" ")[0]
            name = names.get(int(index))
            state["feature"] = f"{index} {name}" if name else index
            print(f"      start {state['feature']}  {glyphs()}")
        elif "end lookup" in body:
            note(f"after {state['feature']}")
        return True

    print(f"=== {case} ({system}, {tag!r}) ===")
    print(f"  codes:  {parseAliases(parsed, system)}")
    print(f"  goal:   {parseWrittenUnits(parsed, composedOTF, language)}")
    buffer.set_message_func(message)
    hb.shape(font, buffer)  # type: ignore
    print(f"  result: {glyphs()}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        print("writing systems:", ", ".join(LANGUAGE))
        raise SystemExit(2)

    system = sys.argv[2] if len(sys.argv) > 2 else "hud"
    if system not in LANGUAGE:
        raise SystemExit(f"unknown writing system {system!r}; one of {', '.join(LANGUAGE)}")
    if not composedOTF.exists():
        raise SystemExit(f"{composedOTF} is missing; run `uv run pytest tests/test_unified.py -s`")
    trace(sys.argv[1], system)


if __name__ == "__main__":
    main()

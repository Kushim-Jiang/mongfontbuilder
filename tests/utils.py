import re
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import yaml
from fontTools import unicodedata
from mongfontbuilder.data import LocaleID, aliases

import data

testsDir = Path(__file__).parent
repo = testsDir / ".."
tempDir = repo / "temp"
tempDir.mkdir(exist_ok=True)

writingSystemToLocaleID: dict[str, LocaleID] = {
    "hud": "MNG",
    "hag": "MNGx",
    "tod": "TOD",
    "tag": "TODx",
    "sib": "SIB",
    "man": "MCH",
    "mag": "MCHx",
}

glyphNameMapping: dict[str, str | None] = {"space": "uni0020.Widespace.nomi"}
for filename in ["marks.yaml", "format-controls.yaml", "bases.yaml"]:
    path = files(data) / filename
    with path.open(encoding="utf-8") as f:
        glyphNameMapping.update(yaml.safe_load(f))


@dataclass
class UTNGlyphName(str):
    """
    Besides the graphical .joining_position, there’s also a joining position in terms of shaping logic that may appear in a glyph name. For example, uni1828.N.init._isol is an isol glyph in terms of shaping, but graphically it’s actually N.init.
    """

    uni_name: str | None
    written_units: list[str]
    joining_position: str | None  # isol | init | medi | fina

    def __init__(self, name: str):
        parts = name.split(".")
        if len(parts) == 1:
            self.uni_name, self.written_units, self.joining_position = parts[0], [], None
            return

        if len(parts) == 3:
            self.uni_name = parts[0]
            written_units_part, self.joining_position = parts[1:]
        else:  # 2
            self.uni_name = None
            written_units_part, self.joining_position = parts
        self.written_units = re.findall("[A-Z][a-z0-9]*", written_units_part)

    def code_point(self) -> int | None:
        if self.uni_name:
            return int(self.uni_name.removeprefix("uni"), 16)
        else:
            return None

    def code_point_agnostic(self) -> str:
        return ".".join(i for i in ["".join(self.written_units), self.joining_position] if i)


def get_units(utn_name: UTNGlyphName) -> str:
    position = utn_name.joining_position or ""
    units: list[str]
    if position.startswith("init"):
        units = utn_name.written_units + ["Right"]
    elif position.startswith("medi"):
        units = ["Left"] + utn_name.written_units + ["Right"]
    elif position.startswith("fina"):
        units = ["Left"] + utn_name.written_units
    else:
        units = utn_name.written_units
    return "".join(units)


def init_to_medi(written_units: str, units: list[str]) -> str:
    for unit in units:
        written_units = written_units.replace(f"{unit}RightLeftSelectRight", f"Left{unit}Right")
    return written_units


def parse_code(text: str, writing_system: str) -> str:
    localeID = writingSystemToLocaleID[writing_system]

    result = []
    for char in text:
        alias = aliases[unicodedata.name(char)]
        if isinstance(alias, str):
            result.append(alias)
        else:
            result.append(alias[localeID])

    return " ".join(result)


def test(codes: str, index: str, result: str, goal: str):
    if result != goal:
        print(f"ind:  {index}")
        print(f"code: {codes}")
        print(f"res:  {result}\ngoal: {goal}\n=====")


def parse_glyphs(text: str, font: Path) -> str:
    from uharfbuzz import Blob, Buffer, Face, Font, shape  # type: ignore

    hbFont = Font(Face(Blob.from_file_path(font)))
    buffer = Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    shape(hbFont, buffer)

    glyph_names = [hbFont.glyph_to_string(info.codepoint) for info in buffer.glyph_infos]
    written_units = ""

    for glyph_name in glyph_names:
        name = glyphNameMapping.get(glyph_name) or glyph_name
        utn_name = UTNGlyphName(name.replace("._", "@").replace(".mvs", "@mvs"))
        written_units += get_units(utn_name)

    written_units = (
        written_units.replace("RightLeft", "")
        .replace("RightBaludaLeft", "Baluda")
        .replace("RightTribaludaLeft", "Tribaluda")
    )
    return (
        " ".join(UTNGlyphName(f".{written_units}.").written_units)
        .replace("Nirugu", "Ni")
        .replace("Left", "<")
        .replace("Right", ">")
        .replace("Widespace", "-")
        .replace("Narrowspace", "_")
    )

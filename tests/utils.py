from importlib.resources import files
from pathlib import Path

import mongfontbuilder
import yaml
from fontTools import unicodedata
from mongfontbuilder import UTNGlyphName
from mongfontbuilder.data import LocaleID, aliases

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
    path = files(mongfontbuilder) / "data" / "glyphs" / filename
    with path.open(encoding="utf-8") as f:
        glyphNameMapping.update(yaml.safe_load(f))


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

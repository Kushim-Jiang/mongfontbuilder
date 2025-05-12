import re
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import yaml
from fontTools import unicodedata
from fontTools.ttLib import TTFont
from mongfontbuilder.data import LocaleID, aliases
from mongfontbuilder.utils import namespaceFromLocale

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

glyphNameMapping: dict[str, str | None] = {
    "space": "uni0020.Widespace.nomi",
    "uni0020": "uni0020.Widespace.nomi",
}
for filename in ["marks.yaml", "format-controls.yaml", "bases.yaml"]:
    path = files(data) / filename
    with path.open(encoding="utf-8") as f:
        glyphNameMapping.update(yaml.safe_load(f))


@dataclass
class UTNGlyphName(str):
    """
    Besides the graphical .joining_position, there’s also a joining position in terms of shaping logic that may appear in a glyph name. For example, uni1828.N.init._isol is an isol glyph in terms of shaping, but graphically it’s actually N.init.
    """

    uniName: str | None
    writtenUnits: list[str]
    joiningPosition: str | None  # isol | init | medi | fina

    def __init__(self, name: str):
        parts = name.split(".")
        if len(parts) == 1:
            self.uniName, self.writtenUnits, self.joiningPosition = parts[0], [], None
            return

        if len(parts) == 3:
            self.uniName = parts[0]
            written_units_part, self.joiningPosition = parts[1:]
        else:  # 2
            self.uniName = None
            written_units_part, self.joiningPosition = parts
        self.writtenUnits = re.findall("[A-Z][a-z0-9]*", written_units_part)

    def codePoint(self) -> int | None:
        if self.uniName:
            return int(self.uniName.removeprefix("uni"), 16)
        else:
            return None

    def codePointAgnostic(self) -> str:
        return ".".join(i for i in ["".join(self.writtenUnits), self.joiningPosition] if i)


def getWrittenUnits(utnName: UTNGlyphName) -> str:
    position = utnName.joiningPosition or ""
    units: list[str]
    if position.startswith("init"):
        units = utnName.writtenUnits + ["Right"]
    elif position.startswith("medi"):
        units = ["Left"] + utnName.writtenUnits + ["Right"]
    elif position.startswith("fina"):
        units = ["Left"] + utnName.writtenUnits
    else:
        units = utnName.writtenUnits
    return "".join(units)


def parseAliases(text: str, writing_system: str) -> str:
    localeID = writingSystemToLocaleID[writing_system]

    result = []
    for char in text:
        alias = aliases[unicodedata.name(char)]
        if isinstance(alias, str):
            result.append(alias)
        else:
            result.append(alias[namespaceFromLocale(localeID)])

    return " ".join(result)


def parseLetter(names: str, writing_system: str) -> str:
    localeID = writingSystemToLocaleID[writing_system]
    result = []

    for name in names.split():
        try:
            charName = next(
                k
                for k, v in aliases.items()
                if (isinstance(v, dict) and v.get(namespaceFromLocale(localeID)) == name)
                or v == name
            )
            result.append(unicodedata.lookup(charName))
        except StopIteration:
            raise ValueError(f"No alias found for name: {name}")

    return "".join(result)


def parseWrittenUnits(text: str, font: Path) -> str:
    from uharfbuzz import Blob, Buffer, Face, Font, shape  # type: ignore

    hbFont = Font(Face(Blob.from_file_path(font)))
    buffer = Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    shape(hbFont, buffer)

    glyphNames = [hbFont.glyph_to_string(info.codepoint) for info in buffer.glyph_infos]
    writtenUnits = ""

    for glyphName in glyphNames:
        name = glyphNameMapping.get(glyphName) or glyphName
        utnName = UTNGlyphName(name.replace("._", "@").replace(".mvs", "@mvs"))
        writtenUnits += getWrittenUnits(utnName)

    writtenUnits = (
        writtenUnits.replace("RightLeft", "")
        .replace("RightBaludaLeft", "Baluda")
        .replace("RightTribaludaLeft", "Tribaluda")
    )
    return (
        " ".join(UTNGlyphName(f".{writtenUnits}.").writtenUnits)
        .replace("Nirugu", "Ni")
        .replace("Left", "<")
        .replace("Right", ">")
        .replace("Widespace", "-")
        .replace("Narrowspace", "_")
    )


def makeFontFilename(font: TTFont) -> str:
    from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e

    table: table__n_a_m_e = font["name"]  # type: ignore
    postScriptName = table.getDebugName(6)
    assert postScriptName

    suffix = ".otf" if {"CFF ", "CFF2"}.intersection(font.keys()) else ".ttf"
    return postScriptName + suffix

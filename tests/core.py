import csv
import os
import sys
import tempfile
from importlib.resources import files
from pathlib import Path

import ufoLib2
from fontTools import unicodedata
from mongfontbuilder.data import aliases
from ufo2ft import compileTTF
from utils import parse_code, parse_glyphs, test, writingSystemToLocaleID

import data


def main() -> None:
    _, font = sys.argv

    for writingSystem in writingSystemToLocaleID:
        path = files(data) / f"core-{writingSystem}.tsv"
        with path.open(encoding="utf-8") as f:
            rules = [i for i in csv.reader(f, delimiter="\t") if i and not i[0].startswith("#")]

        for index, letters, goal in rules:
            text = parse_letter(letters, writingSystem)
            test(
                codes=parse_code(text, writingSystem),
                index=f"{writingSystem}-core > {index}",
                result=parse_glyphs(text, Path(font)),
                goal=goal,
            )


def create_ufo(glyph_list: list[str], otl: str):
    ufo = ufoLib2.Font()
    ufo.info.familyName = "Temp"
    ufo.info.styleName = "Regular"
    for glyph_name in glyph_list:
        _ = ufo.newGlyph(glyph_name)
    ufo.features.text = otl
    return ufo


def build_ttf():
    glyph_list = ["A", "B", "C"]
    otl = """
    # OpenType layout features
    feature liga {
        sub A B by C;
    } liga;
    """
    ufo = create_ufo(glyph_list, otl)

    with tempfile.TemporaryDirectory() as temp_dir:
        ttf = compileTTF(ufo)
        font_path = os.path.join(temp_dir, "Temp-Regular.ttf")
        ttf.save(font_path)


def parse_letter(names: str, writing_system: str) -> str:
    localeID = writingSystemToLocaleID[writing_system]

    result = []
    for name in names.split():
        charName = next(
            k
            for k, v in aliases.items()
            if (isinstance(v, dict) and v.get(localeID) == name) or v == name
        )
        result.append(unicodedata.lookup(charName))

    return "".join(result)


if __name__ == "__main__":
    main()

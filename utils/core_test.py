import csv
import os
import tempfile
from pathlib import Path

import ufoLib2
from ufo2ft import compileTTF

from . import char_yaml, parse_code, repo, test
from .eac_test import parse_glyphs


def _load(path: Path) -> list[list[str]]:
    with path.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        return [line for line in reader if line and not line[0].startswith("#")]


dir_path = Path(__file__).parent.parent
font_path = dir_path / "temp" / "DraftNew-Regular.otf"

writing_systems = ["hud", "hag", "tod", "tag", "sib", "man", "mag"]
rule_tsv = {name: _load(repo / "utils" / "data" / f"{name}-core.tsv") for name in writing_systems}


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
    names_list = names.split(" ")
    result = []

    letters = {v["id"]: k for k, v in char_yaml.get(writing_system, {}).items()}
    others = {v["id"]: k for k, v in char_yaml.get("other", {}).items() if "id" in v}

    for name in names_list:
        id_name = f".{name}"
        if id_name in letters:
            char = chr(letters[id_name])
        elif id_name in others:
            char = chr(others[id_name])
        else:
            raise ValueError(f"'.{name}' not found in '{writing_system}'.")
        result.append(char)
    return "".join(result)


def core_test(writing_system: str):
    set_name = f"{writing_system}-core"
    test_list = rule_tsv.get(writing_system, {})

    for test_item in test_list:
        idx, letters, goal = test_item
        word = parse_letter(letters, writing_system)
        codes = parse_code(word, writing_system)
        result = parse_glyphs(word)
        test(codes, f"{set_name} > {idx}", result, goal)

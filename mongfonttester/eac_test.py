import json
from pathlib import Path

import yaml

from mongfontbuilder import UTNGlyphName
from mongfonttester.test import char_json, get_units, parse_code, shape_text, test


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        if path.suffix == ".json":
            return json.load(f)
        return yaml.load(f, yaml.FullLoader)


def _load_rule_json(dir_path: Path, filenames: dict[str, str]) -> dict:
    return {
        name: _load(dir_path / "references" / filename)
        for name, filename in filenames.items()
    }


dir_path = Path(__file__).parent.parent
font_path = dir_path / "temp" / "DraftNew-Regular.otf"

menk_path = dir_path / "mongfontbuilder" / "data" / "menksoft.yaml"
menk_yaml = _load(menk_path)

rule_filenames = {
    "hud": "xunifont_rulewords_mon.json",
    "tod": "xunifont_rulewords_todo.json",
    "sib": "xunifont_rulewords_sibe.json",
    "man": "xunifont_rulewords_man.json",
}
rule_json = _load_rule_json(dir_path, rule_filenames)


def parse_glyphs(word: str, font: Path = font_path) -> str:
    glyph_names = [glyph.get("glyph_name") for glyph in shape_text(word, font)]
    written_units = ""

    for glyph_name in glyph_names:
        name = (
            char_json.get("base", {}).get(glyph_name)
            or char_json.get("control", {}).get(glyph_name)
            or char_json.get("mark", {}).get(glyph_name)
            or ("uni0020.Widespace.nomi" if glyph_name == "space" else glyph_name)
        )

        utn_name = UTNGlyphName(name.replace("._", "@").replace(".mvs", "@mvs"))
        written_units += get_units(utn_name)

    written_units = written_units.replace("RightLeft", "")
    return (
        " ".join(UTNGlyphName(f".{written_units}.").written_units)
        .replace("Nirugu", "-")
        .replace("Left", "<")
        .replace("Right", ">")
        .replace("Widespace", "_")
    )


def parse_menksoft(shape: str) -> str:
    written_units = ""

    for char in shape:
        name = menk_yaml.get(ord(char))
        while isinstance(name, int):
            name = menk_yaml.get(name)

        utn_name = UTNGlyphName(name.replace(".p", "@p"))
        written_units += get_units(utn_name)

    written_units = written_units.replace("RightLeft", "")
    return (
        " ".join(UTNGlyphName(f".{written_units}.").written_units)
        .replace("Nirugu", "-")
        .replace("Left", "<")
        .replace("Right", ">")
        .replace("Widespace", "_")
    )


def eac_test(writing_system: str):
    set_name = f"eac-{writing_system}"
    rule_list = rule_json.get(writing_system, {}).get("rulelist", [])

    for rule in rule_list:
        rule_index = rule.get("ruleindex", "")
        rule_words = rule.get("rulewords", [])
        for idx, rule_word in enumerate(rule_words, 1):
            word = rule_word.get("word", "")
            if not word or "ignore" in rule_word.get("flag", ""):
                continue

            codes = parse_code(word, writing_system)
            result = parse_glyphs(word)
            shape = rule_word.get("shape", "")
            goal = parse_menksoft(shape)
            test(codes, f"{set_name} > {rule_index} > {idx}", result, goal)

import json
from pathlib import Path

import yaml
from mongfontbuilder import UTNGlyphName

from . import char_json, dataDir, get_units, parse_code, repo, shape_text, test

with (dataDir / "menksoft.yaml").open(encoding="utf-8") as f:
    menk_yaml = yaml.safe_load(f)


rule_json = {
    k: json.loads((repo / "references" / v).read_text(encoding="utf-8"))
    for k, v in {
        "hud": "xunifont_rulewords_mon.json",
        "tod": "xunifont_rulewords_todo.json",
        "sib": "xunifont_rulewords_sibe.json",
        "man": "xunifont_rulewords_man.json",
    }.items()
}


def parse_glyphs(word: str, font: Path = repo / "temp" / "DraftNew-Regular.otf") -> str:
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
        .replace("Nirugu", "Ni")
        .replace("Left", "<")
        .replace("Right", ">")
        .replace("Widespace", "-")
        .replace("Narrowspace", "_")
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

import json
from pathlib import Path
from typing import Any

import uharfbuzz
import yaml

dir_path = Path(__file__).parent
rule_path = dir_path / "references" / "xunifont_rulewords_mon.json"
font_path = dir_path / "temp" / "DraftNew-Regular.otf"
convert_path = dir_path / "mongfontbuilder" / "data" / "menksoft.yaml"


def shape_text(text: str, font=font_path) -> list[dict[str, Any]]:
    blob = uharfbuzz.Blob.from_file_path(font)
    face = uharfbuzz.Face(blob)
    font = uharfbuzz.Font(face)

    buf = uharfbuzz.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()

    features = {"kern": True, "liga": True}
    uharfbuzz.shape(font, buf, features)

    infos = buf.glyph_infos
    positions = buf.glyph_positions

    return [
        {
            "gid": info.codepoint,
            "glyph_name": font.glyph_to_string(info.codepoint),
            "cluster": info.cluster,
            "x_advance": pos.x_advance,
            "x_offset": pos.x_offset,
            "y_offset": pos.y_offset,
        }
        for info, pos in zip(infos, positions)
    ]


def main():
    with rule_path.open(encoding="utf-8") as f:
        rule_json: dict = json.load(f)
    with convert_path.open(encoding="utf-8") as f:
        convert_yaml: dict = yaml.load(f, yaml.FullLoader)

    rule_list: list[dict] = rule_json.get("rulelist") or []

    for rule in rule_list:
        rule_index: str = rule.get("ruleindex") or ""
        rule_words: list[dict] = rule.get("rulewords") or []

        for rule_word in rule_words:
            word: str = rule_word.get("word") or ""
            shape: str = rule_word.get("shape") or ""

            # TODO: glyph names to written units
            result: list[str] = [glyph.get("glyph_name") for glyph in shape_text(word)]
            goal = [convert_yaml.get(ord(char)) for char in shape]
            print(f"index:  {rule_index}\nresult: {result}\ngoal:   {goal}\n=====")


main()

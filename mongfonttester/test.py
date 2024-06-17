import json
from pathlib import Path

import uharfbuzz
import yaml

from mongfontbuilder import UTNGlyphName


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        if path.suffix == ".json":
            return json.load(f)
        return yaml.load(f, yaml.FullLoader)


def load_char_data():
    char_paths = {
        "hud": "locales/hudum/characters.yaml",
        "hag": "locales/hudum-ag/characters.yaml",
        "tod": "locales/todo/characters.yaml",
        "tag": "locales/todo-ag/characters.yaml",
        "sib": "locales/sibe/characters.yaml",
        "man": "locales/manchu/characters.yaml",
        "mag": "locales/manchu-ag/characters.yaml",
        "other": "characters.yaml",
    }

    char_data = {}
    for key, relative_path in char_paths.items():
        char_data[key] = _load(data_path / relative_path)
    return char_data


def load_glyph_data():
    glyph_paths = {
        "base": "glyphs/bases.yaml",
        "control": "glyphs/format-controls.yaml",
        "mark": "glyphs/marks.yaml",
    }

    glyph_data = {}
    for key, relative_path in glyph_paths.items():
        glyph_data[key] = _load(data_path / relative_path)
    return glyph_data


dir_path = Path(__file__).parent.parent
data_path = dir_path / "mongfontbuilder" / "data"
char_yaml = load_char_data()
char_json = load_glyph_data()


def shape_text(text: str, font: Path) -> list[dict]:
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


def get_units(utn_name: UTNGlyphName) -> str:
    units: list[str]
    if utn_name.joining_position.startswith("init"):
        units = utn_name.written_units + ["Right"]
    elif utn_name.joining_position.startswith("medi"):
        units = ["Left"] + utn_name.written_units + ["Right"]
    elif utn_name.joining_position.startswith("fina"):
        units = ["Left"] + utn_name.written_units
    else:
        units = utn_name.written_units
    return "".join(units)


def init_to_medi(written_units: str, units: list[str]) -> str:
    for unit in units:
        written_units = written_units.replace(
            f"{unit}RightLeftSelectRight", f"Left{unit}Right"
        )
    return written_units


def parse_code(word: str, writing_system: str) -> str:
    codes = [ord(char) for char in word]

    result = []
    for code in codes:
        if code in char_yaml.get(writing_system, {}):
            result.append(char_yaml[writing_system][code]["id"][1:])
        elif code in char_yaml.get("other", {}):
            result.append(char_yaml["other"][code]["id"][1:])
        else:
            raise ValueError(hex(code))

    return " ".join(result)


def test(codes: str, index: str, result: str, goal: str):
    if result != goal:
        print(f"ind:  {index}")
        print(f"code: {codes}")
        print(f"res:  {result}\ngoal: {goal}\n=====")

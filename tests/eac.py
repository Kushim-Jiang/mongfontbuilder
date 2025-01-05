import json
import sys
from importlib.resources import files
from pathlib import Path

import yaml
from utils import (
    UTNGlyphName,
    get_units,
    parse_code,
    parse_glyphs,
    test,
    writingSystemToLocaleID,
)

import data


def main() -> None:
    _, font = sys.argv

    for writingSystem in writingSystemToLocaleID:
        path = files(data) / f"eac-{writingSystem}.json"
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as f:
            rules = json.load(f)["rulelist"]

        for rule in rules:
            for index, wordDict in enumerate(rule["rulewords"], 1):
                if wordDict["flag"].get("ignore"):
                    continue
                word = wordDict["word"]
                test(
                    codes=parse_code(word, writingSystem),
                    index=f"eac-{writingSystem} > {rule['ruleindex']} > {index}",
                    result=parse_glyphs(word, Path(font)),
                    goal=parse_menksoft(wordDict["shape"]),
                )


path = files(data) / "menksoft.yaml"
with path.open(encoding="utf-8") as f:
    menksoftData: dict[int, str | int | None] = yaml.safe_load(f)


def parse_menksoft(shape: str) -> str:
    writtenUnits = ""
    for char in shape:
        name = menksoftData[ord(char)]
        while isinstance(name, int):
            name = menksoftData[name]
        assert name
        writtenUnits += get_units(UTNGlyphName(name.replace(".p", "@p")))

    writtenUnits = writtenUnits.replace("RightLeft", "")
    return (
        " ".join(UTNGlyphName(f".{writtenUnits}.").written_units)
        .replace("Nirugu", "Ni")
        .replace("Left", "<")
        .replace("Right", ">")
        .replace("Widespace", "-")
        .replace("Narrowspace", "_")
    )


if __name__ == "__main__":
    main()

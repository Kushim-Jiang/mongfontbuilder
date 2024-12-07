from __future__ import annotations

from dataclasses import dataclass, field
from importlib.resources import files

import yaml

code = "Mong"
characters: dict[int, Character]


@dataclass
class Variant:
    charCp: int
    joiningPosition: str
    writtenUnits: list[str]
    fvs: None | int
    conditions: list[str]
    note: dict

    @classmethod
    def from_data(cls, charCp: int, joiningPosition: str, variantData: dict) -> Variant:
        return cls(
            charCp,
            joiningPosition,
            [_validate_case(i) for i in variantData.get("written_units", [])],
            variantData.get("fvs"),
            variantData.get("conditions", []),
            {
                "eac_index": variantData.get("eac_index", None),
                "gb_index": variantData.get("gb_index", None),
                "note": variantData.get("note", ""),
            },
        )


@dataclass
class Character:
    cp: int
    id: None | str
    variants: dict[str, list[Variant]] = field(default_factory=dict)

    @classmethod
    def from_data(cls, key: int, value: dict[str, dict]) -> Character:
        return cls(
            key,
            _validate_case(value.get("id", ".")),
            {
                joiningPosition: [
                    Variant.from_data(key, joiningPosition, variant)
                    for variant in value.get("variants", {}).get(joiningPosition)
                ]
                for joiningPosition in value.get("variants", {}).keys()
            },
        )


def _validate_case(case: str, /) -> str:
    literal_prefix = "."
    if case.startswith(literal_prefix):
        return case.removeprefix(literal_prefix)
    else:
        raise Exception(f""""{case}" is not a valid case literal""")


path = files(__package__ or "") / "data" / "characters.yaml"

characters = {}
with path.open(encoding="utf-8") as f:
    for k, v in yaml.safe_load(f).items():
        if char := Character.from_data(k, v):
            characters[char.cp] = char

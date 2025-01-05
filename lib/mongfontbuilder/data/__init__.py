import json
from importlib.resources import files

from cattrs import structure

from .constants import JoiningPosition
from .types import (
    FVS,
    Alias,
    CharacterName,
    Locale,
    LocaleID,
    Variant,
    WrittenUnitID,
    WrittenUnitVariant,
)

assert __package__
dir = files(__package__)

with (dir / "writtenUnits.json").open(encoding="utf-8") as f:
    writtenUnits = structure(
        json.load(f),
        dict[WrittenUnitID, dict[JoiningPosition, WrittenUnitVariant]],
    )

with (dir / "locales.json").open(encoding="utf-8") as f:
    locales = structure(
        json.load(f),
        dict[LocaleID, Locale],
    )

with (dir / "aliases.json").open(encoding="utf-8") as f:
    aliases = structure(
        json.load(f),
        dict[CharacterName, Alias],
    )

with (dir / "variants.json").open(encoding="utf-8") as f:
    variants = structure(
        json.load(f),
        dict[CharacterName, dict[JoiningPosition, dict[FVS, Variant]]],
    )

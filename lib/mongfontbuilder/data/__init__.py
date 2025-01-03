import json
from importlib.resources import open_text

from cattrs import structure

from .types import (
    FVS,
    Alias,
    CharacterName,
    JoiningPosition,
    Locale,
    LocaleID,
    Variant,
    WrittenUnitID,
    WrittenUnitVariant,
)

assert __package__

with open_text(__package__, "writtenUnits.json") as f:
    writtenUnits = structure(
        json.load(f),
        dict[WrittenUnitID, dict[JoiningPosition, WrittenUnitVariant]],
    )

with open_text(__package__, "locales.json") as f:
    locales = structure(
        json.load(f),
        dict[LocaleID, Locale],
    )

with open_text(__package__, "aliases.json") as f:
    aliases = structure(
        json.load(f),
        dict[CharacterName, Alias],
    )

with open_text(__package__, "variants.json") as f:
    variants = structure(
        json.load(f),
        dict[CharacterName, dict[JoiningPosition, dict[FVS, Variant]]],
    )

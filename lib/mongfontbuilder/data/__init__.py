import json
from importlib.resources import files
from typing import Literal

from cattrs import structure

from .logic import resolveCmapVariants
from .types import (
    FVS,
    AliasData,
    CharacterName,
    JoiningPosition,
    LocaleData,
    LocaleID,
    VariantData,
    WrittenUnitID,
)

assert __package__
dir = files(__package__)

with (dir / "writtenUnits.json").open(encoding="utf-8") as f:
    writtenUnits: list[WrittenUnitID] = json.load(f)

with (dir / "ligatures.json").open(encoding="utf-8") as f:
    ligatures: dict[
        Literal["required", "optional"],
        dict[str, list[JoiningPosition]],
    ] = json.load(f)

with (dir / "locales.json").open(encoding="utf-8") as f:
    locales = structure(
        json.load(f),
        dict[LocaleID, LocaleData],
    )

with (dir / "aliases.json").open(encoding="utf-8") as f:
    aliases = structure(
        json.load(f),
        dict[CharacterName, AliasData],
    )

with (dir / "variants.json").open(encoding="utf-8") as f:
    variants = structure(
        json.load(f),
        dict[CharacterName, dict[JoiningPosition, dict[FVS, VariantData]]],
    )

with (dir / "particles.json").open(encoding="utf-8") as f:
    particles = structure(json.load(f), dict[LocaleID, dict[str, list[FVS]]])

codePointToCmapVariant = resolveCmapVariants(variants)

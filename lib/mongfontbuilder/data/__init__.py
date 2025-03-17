import json
from importlib.resources import files

from cattrs import structure

from .misc import JoiningPosition
from .types import (
    FVS,
    AliasData,
    CharacterName,
    LocaleData,
    LocaleID,
    VariantData,
    VariantReference,
    WrittenUnitID,
)

assert __package__
dir = files(__package__)

with (dir / "writtenUnits.json").open(encoding="utf-8") as f:
    writtenUnits: list[WrittenUnitID] = json.load(f)

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


def normalizedWritten(
    written: list[str] | VariantReference,
    positionToFVSToVariantData: dict[JoiningPosition, dict[FVS, VariantData]],
) -> tuple[list[WrittenUnitID], JoiningPosition | None]:
    if not isinstance(written, list):
        position, fvs, locale = written
        assert not locale
        written = positionToFVSToVariantData[position][fvs].written
        assert isinstance(written, list)
    else:
        position = None
    return written, position

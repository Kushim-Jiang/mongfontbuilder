import json
from importlib.resources import files
from typing import Literal

from cattrs import structure
from fontTools import unicodedata

from .misc import JoiningPosition, joiningPositions
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


def variantFromReference(
    reference: VariantReference,
    positionToFVSToVariantData: dict[JoiningPosition, dict[FVS, VariantData]],
) -> list[WrittenUnitID]:
    position, fvs, locale = reference
    if not locale:
        written = positionToFVSToVariantData[position][fvs].written
    else:
        written = positionToFVSToVariantData[position][fvs].locales[locale].written
    assert isinstance(written, list)
    return written


def _resolveCmapVariants() -> dict[int, tuple[list[WrittenUnitID], JoiningPosition]]:
    codePointToPositionToVariant = dict[
        int, dict[JoiningPosition, tuple[list[WrittenUnitID], JoiningPosition]]
    ]()
    for charName, positionToFVSToVariantData in variants.items():
        codePoint = ord(unicodedata.lookup(charName))
        for position, fvsToVariantData in positionToFVSToVariantData.items():
            for data in fvsToVariantData.values():
                if data.default:
                    written = data.written
                    if isinstance(written, VariantReference):
                        variant = (
                            variantFromReference(written, positionToFVSToVariantData),
                            written.position,
                        )
                    else:
                        variant = written, position
                    codePointToPositionToVariant.setdefault(codePoint, {})[position] = variant
                    break

    codePointToVariant = dict[int, tuple[list[WrittenUnitID], JoiningPosition]]()
    for codePoint, positionToVariant in sorted(codePointToPositionToVariant.items()):
        for position in joiningPositions:
            if variant := positionToVariant.get(position):
                if variant not in codePointToVariant.values():
                    codePointToVariant[codePoint] = variant
                    break
        else:
            raise NotImplementedError

    return codePointToVariant


codePointToCmapVariant = _resolveCmapVariants()

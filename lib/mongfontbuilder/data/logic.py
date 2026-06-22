from fontTools import unicodedata

from .types import (
    FVS,
    CharacterName,
    JoiningPosition,
    VariantData,
    VariantReference,
    WrittenUnitID,
    joiningPositions,
)


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


def resolveCmapVariants(
    variants: dict[CharacterName, dict[JoiningPosition, dict[FVS, VariantData]]],
) -> dict[int, tuple[list[WrittenUnitID], JoiningPosition]]:
    codePointToPositionToVariant = dict[
        int, dict[JoiningPosition, tuple[list[WrittenUnitID], JoiningPosition]]
    ]()
    for charName, positionToFVSToVariantData in variants.items():
        codePoint = ord(unicodedata.lookup(charName))
        for position in joiningPositions:
            for data in positionToFVSToVariantData[position].values():
                if data.default:
                    cross_locale = True
                    for locale_data in data.locales.values():
                        if locale_data.written:
                            cross_locale = False
                            break
                    if cross_locale:
                        written = data.written
                        if not isinstance(written, VariantReference):
                            variant = written, position
                        else:
                            continue
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

from fontTools import unicodedata

from .types import (
    FVS,
    CharacterName,
    JoiningPosition,
    LocaleID,
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


def choosesVariant(locale: LocaleID, variant: VariantData, condition: str) -> bool:
    """Whether *variant* answers *condition* in *locale*.

    A variant names the conditions of the letters around it that it answers — the harmonic
    gender of its word, say — so the lookup of a condition offers the variants that name it.
    """

    return locale in variant.locales and condition in variant.locales[locale].conditions


def choosesLvs(locale: LocaleID, variant: VariantData) -> bool:
    """Whether *variant* is written with a long vowel sign in *locale*."""

    return locale in variant.locales and variant.locales[locale].lvs


def resolveCmapVariants(
    variants: dict[CharacterName, dict[JoiningPosition, dict[FVS, VariantData]]],
) -> dict[int, tuple[list[WrittenUnitID], JoiningPosition]]:
    """The cross-locale variant of every character that has one, by code point.

    A character that is written differently in every writing system has no cross-locale
    written form, and its code point maps to no glyph of its own.
    """

    codePointToPositionToVariant = dict[
        int, dict[JoiningPosition, tuple[list[WrittenUnitID], JoiningPosition]]
    ]()
    for charName, positionToFVSToVariantData in variants.items():
        codePoint = ord(unicodedata.lookup(charName))
        for position in joiningPositions:
            crossLocaleVariant = getCrossLocaleVariant(positionToFVSToVariantData, position)
            if not crossLocaleVariant:
                continue
            positionToVariant = codePointToPositionToVariant.setdefault(codePoint, {})
            positionToVariant[position] = crossLocaleVariant

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


def getCrossLocaleVariant(
    positionToFVSToVariantData: dict[JoiningPosition, dict[FVS, VariantData]],
    position: JoiningPosition,
) -> tuple[list[WrittenUnitID], JoiningPosition] | None:
    """The default variant of *position* that every writing system writes the same way.

    A default variant that answers no writing system with a written form of its own is
    written the same way in all of them, so it is the cross-locale written form. A variant
    borrowed from another joining position is resolved to the written form it borrows.
    """

    for data in positionToFVSToVariantData[position].values():
        if not data.default:
            continue
        if any(locale_data.written for locale_data in data.locales.values()):
            continue
        written = data.written
        if not isinstance(written, VariantReference):
            return written, position
        units = variantFromReference(written, positionToFVSToVariantData)
        return units, written.position
    return None

from mongfontbuilder.data.types import FVS, Variant, VariantReference
from tptq.feacomposer import FeaComposer

from .data import LocaleID, aliases, locales, variants
from .data.misc import JoiningPosition, joiningPositions


def _getCharacterByAlias(locale: LocaleID, alias: str):
    for character, localeToAlias in aliases.items():
        if isinstance(localeToAlias, str):
            if alias == localeToAlias:
                return character
        else:
            if locale.removesuffix("x") in localeToAlias:
                if alias == localeToAlias[locale.removesuffix("x")]:
                    return character
    raise ValueError(f"no alias {alias} found in {locale}")


def _getWrittenUnits(
    written: list[str] | VariantReference,
    joiningPositionToVariants: dict[JoiningPosition, dict[FVS, Variant]],
):
    if isinstance(written, list):
        return "".join(written)
    else:
        variant = joiningPositionToVariants[written.position][written.fvs]
        return "".join(variant.written)


def compose(requiredLocales: list[LocaleID]) -> FeaComposer:
    c = FeaComposer(
        languageSystems={
            "mong": {"dflt"} | {i.removesuffix("x") for i in requiredLocales},
        }
    )

    ### glyph class definition for letters
    for locale in requiredLocales:
        letterAliases = [alias for aliases in locales[locale].categories.values() for alias in aliases]
        for alias in letterAliases:
            for joiningPosition in joiningPositions:
                c.namedGlyphClass(
                    f"{alias}-{locale}.{joiningPosition}",
                    [
                        f"{alias}-{locale}.{_getWrittenUnits(variantInfo.written, variants[_getCharacterByAlias(locale, alias)])}.{joiningPosition}"
                        for variantInfo in variants[_getCharacterByAlias(locale, alias)][joiningPosition].values()
                    ],
                )
            c.namedGlyphClass(
                f"{alias}-{locale}",
                [f"@{alias}-{locale}.{position}" for position in joiningPositions],
            )

    ### glyph class definition for categories

    ### cursive joining

    defaultForms = {
        "isol": {"uni1820": "uni1820.AA.isol"},
        "init": {"uni1820": "uni1820.AA.init"},
        "medi": {"uni1820": "uni1820.A.medi"},
        "fina": {"uni1820": "uni1820.A.fina"},
    }
    for joiningForm in ["isol", "init", "medi", "fina"]:
        with c.Lookup(feature=joiningForm, name=f"IIa.{joiningForm}"):
            for nominalGlyph, defaultGlyph in defaultForms.get(joiningForm, {}).items():
                c.sub(nominalGlyph, by=defaultGlyph)

    ### rclt

    # control character: preprocessing

    # III.1: Phonetic - Chachlag

    # III.2: Phonetic - Syllabic

    # III.3: Phonetic - Particle

    # III.4: Graphemic - Devsger

    # III.5: Graphemic - Post bowed

    # III.6: Uncaptured - FVS

    # IIb.1: ligature

    # IIb.2: cleanup of format controls

    # IIb.3: optional treatments

    ### vert

    # Ib: vertical punctuation

    ### rlig

    # Ib: punctuation ligature

    ### vpal

    # Ib: proportional punctuation

    ### mark

    # Ib: marks position

    return c

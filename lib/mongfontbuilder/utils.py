import unicodedata
from typing import cast

from .data import JoiningPosition, aliases, locales, variants
from .data.types import FVS, LocaleID, Variant, VariantReference


def removeSuffix(locale: LocaleID) -> LocaleID:
    return cast(LocaleID, locale.removesuffix("x"))


def getCharNameByAlias(locale: LocaleID, alias: str):
    for character, localeToAlias in aliases.items():
        if isinstance(localeToAlias, str):
            if alias == localeToAlias:
                return character
        else:
            if removeSuffix(locale) in localeToAlias:
                if alias == localeToAlias[removeSuffix(locale)]:
                    return character
    raise ValueError(f"no alias {alias} found in {locale}")


def getUniNameByCharName(name: str):
    return "u" + hex(ord(unicodedata.lookup(name))).removeprefix("0x").upper()


def getAliasesByLocale(locale: LocaleID):
    return [alias for aliases in locales[locale].categories.values() for alias in aliases]


def getWrittenUnits(
    written: list[str] | VariantReference,
    joiningPositionToVariants: dict[JoiningPosition, dict[FVS, Variant]],
):
    if isinstance(written, list):
        return "".join(written)
    else:
        return "".join(cast(list, joiningPositionToVariants[written.position][written.fvs].written))


def getDefaultVariant(alias: str, locale: LocaleID, joiningPosition: JoiningPosition):
    fvsToVariant: dict[FVS, Variant] = variants[getCharNameByAlias(locale, alias)][joiningPosition]
    for variant in fvsToVariant.values():
        if locale in variant.locales:
            uniName = getUniNameByCharName(getCharNameByAlias(locale, alias))
            if "default" in variant.locales[locale].conditions:
                writtenUnits = getWrittenUnits(
                    variant.written, variants[getCharNameByAlias(locale, alias)]
                )
                return f"{uniName}.{''.join(writtenUnits)}.{joiningPosition}"

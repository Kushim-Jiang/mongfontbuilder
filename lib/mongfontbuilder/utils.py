from . import GlyphDescriptor, data
from .data.types import CharacterName, JoiningPosition, LocaleID, LocaleNamespace


def namespaceFromLocale(locale: LocaleID) -> LocaleNamespace:
    return locale.removesuffix("x")  # type: ignore


def getCharNameByAlias(locale: LocaleID, alias: str) -> CharacterName:
    namespace = namespaceFromLocale(locale)
    for character, aliasCandidate in data.aliases.items():
        if isinstance(aliasCandidate, str):
            if alias == aliasCandidate:
                return character
        elif alias == aliasCandidate.get(namespace):
            return character
    raise ValueError(f"no alias {alias} found in {locale}")


def getAliasesByLocale(locale: LocaleID) -> list[str]:
    return [alias for aliases in data.locales[locale].categories.values() for alias in aliases]


def getDefaultVariant(locale: LocaleID, alias: str, position: JoiningPosition) -> GlyphDescriptor:
    charName = getCharNameByAlias(locale, alias)
    for variant in data.variants[charName][position].values():
        if localeData := variant.locales.get(locale):
            if "default" in localeData.conditions:
                return GlyphDescriptor.fromData(charName, position, variant)
    raise StopIteration(locale, alias, position)

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
    categories = data.locales[locale].categories
    return categories["vowel"] + categories["consonant"]

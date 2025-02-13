import re

from fontTools import unicodedata
from fontTools.feaLib import ast
from tptq.feacomposer import FeaComposer

from . import GlyphDescriptor, data, uNameFromCodePoint
from .data.misc import joiningPositions
from .data.types import LocaleID
from .utils import getAliasesByLocale, getCharNameByAlias, namespaceFromLocale


def compose(locales: list[LocaleID]) -> FeaComposer:
    c = FeaComposer(
        languageSystems={
            "mong": {"dflt"} | {namespaceFromLocale(i).ljust(4) for i in locales},
        }
    )

    at = composeClasses(c, locales)
    conditions = composeConditions(c, locales, at)

    ### cursive joining
    localeSet = {*locales}
    for position in joiningPositions:
        with c.Lookup(f"IIa.{position}", feature=position):
            for charName, positionToFVSToVariant in data.variants.items():
                if any(
                    localeSet.intersection(i.locales)
                    for i in positionToFVSToVariant[position].values()
                ):
                    c.sub(
                        uNameFromCodePoint(ord(unicodedata.lookup(charName))),
                        by=str(GlyphDescriptor.fromData(charName, position)),
                    )

    ### rclt

    # control character: preprocessing

    with c.Lookup("_.ignored") as _ignored:
        c.sub("nirugu", by="nirugu.ignored")
        c.sub("zwj", by="zwj.ignored")
        c.sub("zwnj", by="zwnj.ignored")

        if {"TOD", "TODx"}.intersection(locales):
            c.sub(at["TOD:lvs"], by="lvs.ignored")

        for i in range(1, 5):
            for suffix in ["", ".effective"]:
                c.sub(f"fvs{i}{suffix}", by=f"fvs{i}.ignored")

    with c.Lookup("_.effective") as _effective:
        for i in range(1, 5):
            for suffix in ["", ".ignored"]:
                c.sub(f"fvs{i}{suffix}", by=f"fvs{i}.effective")

    with c.Lookup("_.nominal") as _nominal:
        for mvs in ["mvs", "mvs.narrow", "mvs.wide"]:
            c.sub(mvs, by="mvs.nominal")
        for mcs in [
            "nirugu.ignored",
            "fvs1.ignored",
            "fvs1.effective",
            "fvs2.ignored",
            "fvs2.effective",
            "fvs3.ignored",
            "fvs3.effective",
            "fvs4.ignored",
            "fvs4.effective",
        ]:
            c.sub(mcs, by=mcs.split(".")[0])

    with c.Lookup("_.narrow") as _narrow:
        for mvs in ["mvs", "mvs.wide", "mvs.nominal", "nnbsp"]:
            c.sub(mvs, by="mvs.narrow")

    with c.Lookup("_.wide") as _wide:
        for mvs in ["mvs", "mvs.narrow", "mvs.nominal", "nnbsp"]:
            c.sub(mvs, by="mvs.wide")

    with c.Lookup("III.controls.preprocessing", feature="rclt"):
        c.contextualSub(c.input("mvs", _nominal))
        c.contextualSub(c.input(c.glyphClass(["zwnj", "zwj", "nirugu", at["fvs"]]), _ignored))

    if "TOD" in locales:
        with c.Lookup("III.TOD.lvs.preprocessing", feature="rclt", flags={"IgnoreMarks": True}):
            c.contextualSub(
                c.input(
                    c.glyphClass([at["TOD:consonant.medi"], at["TOD:vowel.medi"]]),
                    conditions["TOD.fina"],
                ),
                c.input(at["TOD:lvs.fina"], _ignored),
            )
            c.contextualSub(c.input(at["TOD:lvs"], _ignored))

    if "TODx" in locales:
        with c.Lookup("III.TODx.lvs.preprocessing", feature="rclt", flags={"IgnoreMarks": True}):
            c.contextualSub(
                c.input(
                    c.glyphClass([at["TODx:consonant.medi"], at["TODx:vowel.medi"]]),
                    conditions["TODx.fina"],
                ),
                c.input(at["TODx:lvs.fina"], _ignored),
            )
            c.contextualSub(c.input(at["TODx:lvs"], _ignored))

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


def composeClasses(c: FeaComposer, locales: list[LocaleID]) -> dict[str, ast.GlyphClassDefinition]:
    """
    Glyph class definition for letters and categories.
    """

    fvses = [f"fvs{i}" for i in range(1, 5)]

    namedClasses = {
        "msc": c.namedGlyphClass("msc", ["mvs", "mvs.narrow", "mvs.wide", "mvs.nominal", "nnbsp"]),
        "msc.effective": c.namedGlyphClass("msc.effective", ["mvs.narrow", "mvs.wide"]),
        "fvs.nominal": c.namedGlyphClass("fvs.nominal", fvses),
        "fvs.effective": c.namedGlyphClass("fvs.effective", [i + ".effective" for i in fvses]),
        "fvs.ignored": c.namedGlyphClass("fvs.ignored", [i + ".ignored" for i in fvses]),
        "fvs": c.namedGlyphClass(
            "fvs", [c.namedGlyphClass(i, [i, i + ".effective", i + ".ignored"]) for i in fvses]
        ),
    }

    for locale in locales:

        categoryToClasses = dict[str, list[ast.GlyphClassDefinition]]()
        for alias in getAliasesByLocale(locale):
            charName = getCharNameByAlias(locale, alias)
            letter = locale + ":" + alias
            category = next(k for k, v in data.locales[locale].categories.items() if alias in v)
            genderNeutralCategory = re.sub("[A-Z][a-z]+", "", category)

            positionalClasses = list[ast.GlyphClassDefinition]()
            for position, variants in data.variants[charName].items():
                positionalClass = c.namedGlyphClass(
                    letter + "." + position,
                    [
                        str(GlyphDescriptor.fromData(charName, position, i))
                        for i in variants.values()
                    ],
                )
                namedClasses[letter + "." + position] = positionalClass
                positionalClasses.append(positionalClass)
                categoryToClasses.setdefault(
                    locale + ":" + genderNeutralCategory + "." + position, []
                ).append(positionalClass)

            letterClass = c.namedGlyphClass(letter, positionalClasses)
            namedClasses[letter] = letterClass
            if genderNeutralCategory != category:
                categoryToClasses.setdefault(locale + ":" + genderNeutralCategory, []).append(
                    letterClass
                )
            categoryToClasses.setdefault(locale + ":" + category, []).append(letterClass)

        for name, positionalClasses in categoryToClasses.items():
            namedClasses[name] = c.namedGlyphClass(name, positionalClasses)

    return namedClasses


def composeConditions(
    c: FeaComposer, locales: list[LocaleID], at: dict[str, ast.GlyphClassDefinition]
) -> dict[str, ast.LookupBlock]:
    """
    Lookup definition for conditions.
    """
    conditionLookups = {}

    for locale in locales:
        for conditionID in data.locales[locale].conditions:
            with c.Lookup(f"condition.{locale}.{conditionID}") as condition:
                for alias in getAliasesByLocale(locale):
                    charName = getCharNameByAlias(locale, alias)
                    letter = locale + ":" + alias
                    for position, fvsToVariant in data.variants[charName].items():
                        for variant in fvsToVariant.values():
                            if (
                                locale in variant.locales
                                and conditionID in variant.locales[locale].conditions
                            ):
                                c.sub(
                                    at[letter + "." + position],
                                    by=str(GlyphDescriptor.fromData(charName, position, variant)),
                                )
            conditionLookups[f"{locale}.{conditionID}"] = condition

    for locale in ["TOD", "TODx"]:
        if locale in locales:
            with c.Lookup(f"condition.{locale}.{position}") as condition:
                for charName, positionToFVSToVariant in data.variants.items():
                    if any(
                        {locale}.intersection(i.locales)
                        for i in positionToFVSToVariant[position].values()
                    ):
                        c.sub(
                            uNameFromCodePoint(ord(unicodedata.lookup(charName))),
                            by=str(GlyphDescriptor.fromData(charName, position)),
                        )
            conditionLookups[f"{locale}.{position}"] = condition

    return conditionLookups

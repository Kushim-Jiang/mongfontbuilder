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

    composeClasses(c, locales)

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
        c.sub("@lvs-tod", by="lvs.ignored")
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
        c.contextualSub(c.input(c.glyphClass(["zwnj", "zwj", "nirugu", "@fvs"]), _ignored))

    # if {"TOD", "TODx"}.intersection(locales):
    #     with c.Lookup("III.tod_tag.lvs.preprocessing", feature="rclt", flags={"IgnoreMarks": True}):
    #         ...

    # lookup III.tod_tag.lvs.preprocessing {
    #     lookupflag IgnoreMarks;
    #     sub [@tod.consonant.medi @tod.vowel.medi @tag.consonant.medi @tag.vowel.medi]' lookup condition.tod_tag.fina @lvs-tod.fina' lookup _.ignored;
    #     sub [@tod.consonant.init @tod.vowel.init @tag.consonant.init @tag.vowel.init]' lookup condition.tod_tag.isol @lvs-tod.fina' lookup _.ignored;
    #     sub @lvs-tod' lookup _.ignored;
    #     lookupflag 0;
    # } III.tod_tag.lvs.preprocessing;

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


def composeClasses(c: FeaComposer, locales: list[LocaleID]) -> None:
    """
    Glyph class definition for letters and categories.
    """

    c.namedGlyphClass("msc", ["mvs", "mvs.narrow", "mvs.wide", "mvs.nominal", "nnbsp"])
    c.namedGlyphClass("msc.effective", ["mvs.narrow", "mvs.wide"])

    fvses = [f"fvs{i}" for i in range(1, 5)]
    c.namedGlyphClass("fvs.nominal", fvses)
    c.namedGlyphClass("fvs.effective", [i + ".effective" for i in fvses])
    c.namedGlyphClass("fvs.ignored", [i + ".ignored" for i in fvses])
    c.namedGlyphClass(
        "fvs", [c.namedGlyphClass(i, [i, i + ".effective", i + ".ignored"]) for i in fvses]
    )

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
                positionalClasses.append(positionalClass)
                categoryToClasses.setdefault(
                    locale + ":" + genderNeutralCategory + "." + position, []
                ).append(positionalClass)

            letterClass = c.namedGlyphClass(letter, positionalClasses)
            if genderNeutralCategory != category:
                categoryToClasses.setdefault(locale + ":" + genderNeutralCategory, []).append(
                    letterClass
                )
            categoryToClasses.setdefault(locale + ":" + category, []).append(letterClass)

        for name, positionalClasses in categoryToClasses.items():
            c.namedGlyphClass(name, positionalClasses)

from tptq.feacomposer import FeaComposer

from .data import LocaleID, locales, variants
from .data.misc import joiningPositions
from .utils import (
    getAliasesByLocale,
    getCharNameByAlias,
    getDefaultVariant,
    getUniNameByCharName,
    getWrittenUnits,
    removeSuffix,
)


def compose(requiredLocales: list[LocaleID]) -> FeaComposer:
    c = FeaComposer(
        languageSystems={
            "mong": {"dflt"} | {i.removesuffix("x") for i in requiredLocales},
        }
    )

    ### glyph class definition for letters
    for locale in requiredLocales:
        for letterAlias in getAliasesByLocale(locale):
            for joiningPosition in joiningPositions:
                c.namedGlyphClass(
                    f"{letterAlias}-{removeSuffix(locale)}.{joiningPosition}",
                    [
                        f"{getUniNameByCharName(getCharNameByAlias(locale, letterAlias))}.{getWrittenUnits(variantInfo.written, variants[getCharNameByAlias(locale, letterAlias)])}.{joiningPosition}"
                        for variantInfo in variants[getCharNameByAlias(locale, letterAlias)][
                            joiningPosition
                        ].values()
                    ],
                )
            c.namedGlyphClass(
                f"{letterAlias}-{removeSuffix(locale)}",
                [
                    f"@{letterAlias}-{removeSuffix(locale)}.{position}"
                    for position in joiningPositions
                ],
            )

    ### glyph class definition for categories
    for locale in requiredLocales:
        for category in locales[locale].categories.keys():
            c.namedGlyphClass(
                f"{locale}.{category}",
                [
                    f"@{value}-{removeSuffix(locale)}"
                    for value in locales[locale].categories[category]
                ],
            )

    # @MNG.consonantInit
    # @MNG.consonantMedi
    # @MNG.vowel
    # @MNG.vowelMedi
    # @MNG.vowelFina
    # @MNGx.consonantInit
    # @MNGx.consonantMedi
    # @MNGx.vowel
    # @TOD.consonantInit
    # @TOD.consonantMedi
    # @TOD.consonantFina
    # @TOD.vowel
    # @TOD.vowelInit
    # @TOD.vowelMedi
    # @TOD.vowelFina
    # @TODx.consonantInit
    # @TODx.consonantMedi
    # @TODx.vowel
    # @TODx.vowelInit
    # @TODx.vowelMedi
    # @SIB.consonantInit
    # @SIB.vowel
    # @MCH.consonantInit
    # @MCH.vowel
    # @MCHx.consonantInit
    # @MCHx.vowel

    c.namedGlyphClass("msc", ["mvs", "mvs.narrow", "mvs.wide", "mvs.nominal", "nnbsp"])
    c.namedGlyphClass("msc.effective", ["mvs.narrow", "mvs.wide"])

    c.namedGlyphClass("fvs.nominal", [f"fvs{i}" for i in range(1, 5)])
    c.namedGlyphClass("fvs.effective", [f"fvs{i}.effective" for i in range(1, 5)])
    c.namedGlyphClass("fvs.ignored", [f"fvs{i}.ignored" for i in range(1, 5)])
    for i in range(1, 5):
        c.namedGlyphClass(f"fvs{i}", [f"fvs{i} fvs{i}.effective fvs{i}.ignored"])
    c.namedGlyphClass("fvs", [f"@fvs{i}" for i in range(1, 5)])

    # @consonant
    # @consonantInit
    # @vowelMasculine
    # @vowelFeminine
    # @vowelNeuter
    # @vowel

    ### cursive joining
    charToDefaultVariant = {joiningPosition: {} for joiningPosition in joiningPositions}
    for locale in requiredLocales:
        for joiningPosition in joiningPositions:
            for letterAlias in getAliasesByLocale(locale):
                charToDefaultVariant[joiningPosition][
                    getUniNameByCharName(getCharNameByAlias(locale, letterAlias))
                ] = getDefaultVariant(letterAlias, locale, joiningPosition)
    for joiningPosition in joiningPositions:
        with c.Lookup(feature=joiningPosition, name=f"IIa.{joiningPosition}"):
            for nominalGlyph, defaultGlyph in charToDefaultVariant[joiningPosition].items():
                c.sub(nominalGlyph, by=defaultGlyph)

    ### rclt

    # control character: preprocessing

    with c.Lookup("_.ignored") as __ignored:
        c.sub("nirugu", by="nirugu.ignored")
        c.sub("zwj", by="zwj.ignored")
        c.sub("zwnj", by="zwnj.ignored")
        c.sub("@lvs-tod", by="lvs.ignored")
        for i in range(1, 5):
            for suffix in ["", ".effective"]:
                c.sub(f"fvs{i}{suffix}", by=f"fvs{i}.ignored")

    with c.Lookup("_.effective") as __effective:
        for i in range(1, 5):
            for suffix in ["", ".ignored"]:
                c.sub(f"fvs{i}{suffix}", by=f"fvs{i}.effective")

    with c.Lookup("_.nominal") as __nominal:
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

    with c.Lookup("_.narrow") as __narrow:
        for mvs in ["mvs", "mvs.wide", "mvs.nominal", "nnbsp"]:
            c.sub(mvs, by="mvs.narrow")

    with c.Lookup("_.wide") as __wide:
        for mvs in ["mvs", "mvs.narrow", "mvs.nominal", "nnbsp"]:
            c.sub(mvs, by="mvs.wide")

    # lookup III.controls.preprocessing {
    #     sub [zwnj nirugu]' lookup _.ignored;
    #     sub [@vowel @consonant @lvs-tod] zwj' lookup _.ignored [@vowel @consonant @lvs-tod];
    #     sub @fvs' lookup _.ignored;
    #     sub mvs' lookup _.nominal;
    # } III.controls.preprocessing;

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

import re
from dataclasses import dataclass

from fontTools import unicodedata
from fontTools.feaLib import ast
from tptq.feacomposer import FeaComposer

from . import GlyphDescriptor, data, uNameFromCodePoint
from .data.misc import joiningPositions
from .data.types import LocaleID
from .utils import getAliasesByLocale, getCharNameByAlias, namespaceFromLocale


@dataclass
class MongFeaComposer(FeaComposer):
    locales: list[LocaleID]
    classes: dict[str, ast.GlyphClassDefinition]
    conditions: dict[str, ast.LookupBlock]

    def __init__(self, locales: list[LocaleID]) -> None:
        for locale in locales:
            assert locale.removesuffix("x") in locales
        super().__init__(
            languageSystems={"mong": {"dflt"} | {namespaceFromLocale(i).ljust(4) for i in locales}}
        )
        self.locales = locales
        self.classes = self.composeClasses()
        self.conditions = self.composeConditionLookups()

        c = self
        at = self.classes

        ### [Ia] nnbsp -> mvs

        c.comment("Ia: nnbsp -> mvs")
        with c.Lookup("Ia.nnbsp.preprocessing", feature="ccmp"):
            c.sub("nnbsp", by="mvs")

        ### [IIa] cursive joining

        c.comment("IIa: cursive joining")
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

        ### [III.0] control character preprocessing

        c.comment("III.0: control character preprocessing")
        with c.Lookup("_.ignored") as _ignored:
            c.sub("nirugu", by="nirugu.ignored")
            c.sub("zwj", by="zwj.ignored")
            c.sub("zwnj", by="zwnj.ignored")

            if {"TOD", "TODx"}.intersection(locales):
                c.sub(at["TOD:lvs"], by="lvs.ignored")

            for i in range(1, 5):
                for suffix in ["", ".valid"]:
                    c.sub(f"fvs{i}{suffix}", by=f"fvs{i}.ignored")

        with c.Lookup("_.valid") as _valid:
            for i in range(1, 5):
                for suffix in ["", ".ignored"]:
                    c.sub(f"fvs{i}{suffix}", by=f"fvs{i}.valid")

        with c.Lookup("_.invalid") as _invalid:
            for mvs in ["mvs.narrow", "mvs.wide"]:
                c.sub(mvs, by="mvs")
            c.sub("nirugu.ignored", by="nirugu")
            for fvs in [
                "fvs1.ignored",
                "fvs1.valid",
                "fvs2.ignored",
                "fvs2.valid",
                "fvs3.ignored",
                "fvs3.valid",
                "fvs4.ignored",
                "fvs4.valid",
            ]:
                c.sub(fvs, by=fvs.split(".")[0])

        with c.Lookup("_.narrow") as _narrow:
            for mvs in ["mvs", "mvs.wide", "nnbsp"]:
                c.sub(mvs, by="mvs.narrow")

        with c.Lookup("_.wide") as _wide:
            for mvs in ["mvs", "mvs.narrow", "nnbsp"]:
                c.sub(mvs, by="mvs.wide")

        with c.Lookup("III.controls.preprocessing", feature="rclt"):
            c.contextualSub(c.input("mvs", _invalid))
            c.contextualSub(c.input(c.glyphClass(["zwnj", "zwj", "nirugu", at["fvs"]]), _ignored))

        for locale in ["TOD", "TODx"]:
            if locale in locales:
                with c.Lookup(
                    f"III.{locale}.lvs.preprocessing", feature="rclt", flags={"IgnoreMarks": True}
                ):
                    c.contextualSub(
                        c.input(
                            c.glyphClass(
                                [at[f"{locale}:consonant.medi"], at[f"{locale}:vowel.medi"]]
                            ),
                            self.conditions[f"{locale}.fina"],
                        ),
                        c.input(at[f"{locale}:lvs.fina"], _ignored),
                    )
                    c.contextualSub(c.input(at[f"{locale}:lvs"], _ignored))

        ### [III.1] Phonetic - Chachlag

        c.comment("III.1: phonetic - chachlag")
        if "MNG" in locales:
            with c.Lookup("III.MNG.a_e.chachlag", feature="rclt", flags={"IgnoreMarks": True}):
                c.contextualSub(
                    c.input(at["mvs"], _narrow),
                    c.input(
                        c.glyphClass([at["MNG:a.isol"], at["MNG:e.isol"]]),
                        self.conditions["MNG.chachlag"],
                    ),
                )

            with c.Lookup(
                "III.eac.a_e.chachlag", feature="rclt", flags={"UseMarkFilteringSet": at["fvs"]}
            ):
                c.contextualSub(
                    c.input(at["mvs"], _invalid),
                    c.glyphClass([at["MNG:a.isol"], at["MNG:e.isol"]]),
                    at["fvs"],
                )

        # III.2: Phonetic - Syllabic

        if {"MNG", "MNGx", "MCH", "MCHx", "SIB"}.intersection(locales):
            with c.Lookup(
                "III.MNG_MNGx_SIB_MCH_MCHx.o_u_oe_ue.marked",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                if "MNG" in locales:
                    c.contextualSub(
                        at["MNG:consonant.init"],
                        c.input(
                            c.glyphClass([at["MNG:o"], at["MNG:u"], at["MNG:oe"], at["MNG:ue"]]),
                            self.conditions["MNG.marked"],
                        ),
                    )
                if "MNGx" in locales:
                    c.contextualSub(
                        at["MNGx:consonant.init"],
                        c.input(
                            c.glyphClass([at["MNGx:o"], at["MNGx:ue"]]),
                            self.conditions["MNGx.marked"],
                        ),
                    )
                    c.contextualSub(
                        at["MNGx:consonant.init"],
                        at["MNGx:hX"],
                        c.input(at["MNGx:ue"], self.conditions["MNGx.marked"]),
                    )
                for locale in ["SIB", "MCH", "MCHx"]:
                    if locale in locales:
                        c.contextualSub(
                            at[f"{locale}:consonant.init"],
                            c.input(
                                c.glyphClass([at[f"{locale}:o"], at[f"{locale}:u"]]),
                                self.conditions[f"{locale}.marked"],
                            ),
                        )

        if "MNG" in locales:
            with c.Lookup(
                "III.eac.o_u_oe_ue.marked", feature="rclt", flags={"UseMarkFilteringSet": at["fvs"]}
            ):
                oMedi = c.glyphClass(
                    [at["MNG:o.medi"], at["MNG:u.medi"], at["MNG:oe.medi"], at["MNG:ue.medi"]]
                )
                oFina = c.glyphClass(
                    [at["MNG:o.fina"], at["MNG:u.fina"], at["MNG:oe.fina"], at["MNG:ue.fina"]]
                )
                c.contextualSub(at["fvs"], c.input(oMedi, self.conditions["eac.medi"]))
                c.contextualSub(at["fvs"], c.input(oFina, self.conditions["eac.fina"]))
                c.contextualSub(c.input(oMedi, self.conditions["eac.medi"]), at["fvs"])
                c.contextualSub(c.input(oFina, self.conditions["eac.fina"]), at["fvs"])

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

    def composeClasses(self) -> dict[str, ast.GlyphClassDefinition]:
        """
        Glyph class definition for letters and categories.
        """

        classes = dict[str, ast.GlyphClassDefinition]()

        fvses = [f"fvs{i}" for i in range(1, 5)]
        for fvs in fvses:
            classes[fvs] = self.namedGlyphClass(fvs, [fvs, fvs + ".valid", fvs + ".ignored"])
        for name, items in {
            "mvs": ["mvs", "mvs.narrow", "mvs.wide", "nnbsp"],
            "mvs.valid": ["mvs.narrow", "mvs.wide"],
            "fvs.nominal": fvses,
            "fvs.valid": [i + ".valid" for i in fvses],
            "fvs.ignored": [i + ".ignored" for i in fvses],
            "fvs": [classes[i] for i in fvses],
        }.items():
            classes[name] = self.namedGlyphClass(name, items)

        for locale in self.locales:
            categoryToClasses = dict[str, list[ast.GlyphClassDefinition]]()
            for alias in getAliasesByLocale(locale):
                charName = getCharNameByAlias(locale, alias)
                letter = locale + ":" + alias
                category = next(k for k, v in data.locales[locale].categories.items() if alias in v)
                genderNeutralCategory = re.sub("[A-Z][a-z]+", "", category)

                positionalClasses = list[ast.GlyphClassDefinition]()
                for position, variants in data.variants[charName].items():
                    positionalClass = self.namedGlyphClass(
                        letter + "." + position,
                        [
                            str(GlyphDescriptor.fromData(charName, position, i))
                            for i in variants.values()
                        ],
                    )
                    classes[letter + "." + position] = positionalClass
                    positionalClasses.append(positionalClass)
                    categoryToClasses.setdefault(
                        locale + ":" + genderNeutralCategory + "." + position, []
                    ).append(positionalClass)

                letterClass = self.namedGlyphClass(letter, positionalClasses)
                classes[letter] = letterClass
                if genderNeutralCategory != category:
                    categoryToClasses.setdefault(locale + ":" + genderNeutralCategory, []).append(
                        letterClass
                    )
                categoryToClasses.setdefault(locale + ":" + category, []).append(letterClass)

            for name, positionalClasses in categoryToClasses.items():
                classes[name] = self.namedGlyphClass(name, positionalClasses)

        return classes

    def composeConditionLookups(self) -> dict[str, ast.LookupBlock]:
        """
        Lookup definition for conditions.
        """

        lookups = dict[str, ast.LookupBlock]()

        for locale in self.locales:
            for conditionID in data.locales[locale].conditions:
                with self.Lookup(f"{locale}.{conditionID}") as lookup:
                    for alias in getAliasesByLocale(locale):
                        charName = getCharNameByAlias(locale, alias)
                        letter = locale + ":" + alias
                        for position, fvsToVariant in data.variants[charName].items():
                            for variant in fvsToVariant.values():
                                if (
                                    locale in variant.locales
                                    and conditionID in variant.locales[locale].conditions
                                ):
                                    self.sub(
                                        self.classes[letter + "." + position],
                                        by=str(
                                            GlyphDescriptor.fromData(charName, position, variant)
                                        ),
                                    )
                lookups[lookup.name] = lookup

        localeToLookup = {"MNG": "eac", "TOD": "TOD", "TODx": "TODx"}
        for locale in ["MNG", "TOD", "TODx"]:
            if locale in self.locales:
                for position in joiningPositions:
                    with self.Lookup(f"{localeToLookup[locale]}.{position}") as lookup:
                        for charName, positionToFVSToVariant in data.variants.items():
                            if any(
                                locale in i.locales
                                for i in positionToFVSToVariant[position].values()
                            ):
                                self.sub(
                                    uNameFromCodePoint(ord(unicodedata.lookup(charName))),
                                    by=str(GlyphDescriptor.fromData(charName, position)),
                                )
                    lookups[lookup.name] = lookup

        return lookups

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

        self.locales = locales
        super().__init__(
            languageSystems={
                "mong": {"dflt"} | {namespaceFromLocale(i).ljust(4) for i in self.locales}
            }
        )
        self.classes = self.initClasses()
        self.conditions = self.initConditionLookups()

        self.ia()
        self.iia()
        self.iii()

        # IIb.1: ligature
        # IIb.2: cleanup of format controls
        # IIb.3: optional treatments

        # Ib: vertical punctuation
        # Ib: punctuation ligature
        # Ib: proportional punctuation
        # Ib: marks position

    def initClasses(self) -> dict[str, ast.GlyphClassDefinition]:
        """
        Glyph classes.
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

        # Letters and categories:

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

    def initConditionLookups(self) -> dict[str, ast.LookupBlock]:
        """
        Lookups for conditions.
        """

        lookups = dict[str, ast.LookupBlock]()

        for locale in self.locales:
            for condition in data.locales[locale].conditions:
                with self.Lookup(f"{locale}:{condition}") as lookup:
                    for alias in getAliasesByLocale(locale):
                        charName = getCharNameByAlias(locale, alias)
                        letter = locale + ":" + alias
                        for position, fvsToVariant in data.variants[charName].items():
                            for variant in fvsToVariant.values():
                                if (
                                    locale in variant.locales
                                    and condition in variant.locales[locale].conditions
                                ):
                                    self.sub(
                                        self.classes[letter + "." + position],
                                        by=str(
                                            GlyphDescriptor.fromData(charName, position, variant)
                                        ),
                                    )
                lookups[lookup.name] = lookup

            if locale in ["MNG", "TOD", "TODx"]:
                with self.Lookup(f"{locale}:default") as lookup:
                    for position in joiningPositions:
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

    def ia(self) -> None:
        """
        [Ia] nnbsp -> mvs
        """

        with self.Lookup("Ia.nnbsp.preprocessing", feature="ccmp"):
            self.sub("nnbsp", by="mvs")

    def iia(self) -> None:
        """
        [IIa] cursive joining
        """

        localeSet = {*self.locales}
        for position in joiningPositions:
            with self.Lookup(f"IIa.{position}", feature=position):
                for charName, positionToFVSToVariant in data.variants.items():
                    if any(
                        localeSet.intersection(i.locales)
                        for i in positionToFVSToVariant[position].values()
                    ):
                        self.sub(
                            uNameFromCodePoint(ord(unicodedata.lookup(charName))),
                            by=str(GlyphDescriptor.fromData(charName, position)),
                        )

    def iii(self) -> None:
        ### [III.0] control character preprocessing

        c = self
        at = self.classes

        with c.Lookup("_.ignored") as _ignored:
            c.sub("nirugu", by="nirugu.ignored")
            c.sub("zwj", by="zwj.ignored")
            c.sub("zwnj", by="zwnj.ignored")

            if {"TOD", "TODx"}.intersection(self.locales):
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
            if locale in self.locales:
                with c.Lookup(
                    f"III.{locale}.lvs.preprocessing", feature="rclt", flags={"IgnoreMarks": True}
                ):
                    c.contextualSub(
                        c.input(
                            c.glyphClass(
                                [at[f"{locale}:consonant.medi"], at[f"{locale}:vowel.medi"]]
                            ),
                            self.conditions[f"{locale}:default"],
                        ),
                        c.input(at[f"{locale}:lvs.fina"], _ignored),
                    )
                    c.contextualSub(c.input(at[f"{locale}:lvs"], _ignored))

        ### [III.1] Phonetic - Chachlag

        if "MNG" in self.locales:
            with c.Lookup("III.MNG.a_e.chachlag", feature="rclt", flags={"IgnoreMarks": True}):
                c.contextualSub(
                    c.input(at["mvs"], _narrow),
                    c.input(
                        c.glyphClass([at["MNG:a.isol"], at["MNG:e.isol"]]),
                        self.conditions["MNG:chachlag"],
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

        if {"MNG", "MNGx", "MCH", "MCHx", "SIB"}.intersection(self.locales):
            with c.Lookup(
                "III.MNG_MNGx_SIB_MCH_MCHx.o_u_oe_ue.marked",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                if "MNG" in self.locales:
                    c.contextualSub(
                        at["MNG:consonant.init"],
                        c.input(
                            c.glyphClass([at["MNG:o"], at["MNG:u"], at["MNG:oe"], at["MNG:ue"]]),
                            self.conditions["MNG:marked"],
                        ),
                    )
                if "MNGx" in self.locales:
                    c.contextualSub(
                        at["MNGx:consonant.init"],
                        c.input(
                            c.glyphClass([at["MNGx:o"], at["MNGx:ue"]]),
                            self.conditions["MNGx:marked"],
                        ),
                    )
                    c.contextualSub(
                        at["MNGx:consonant.init"],
                        at["MNGx:hX"],
                        c.input(at["MNGx:ue"], self.conditions["MNGx:marked"]),
                    )
                for locale in ["SIB", "MCH", "MCHx"]:
                    if locale in self.locales:
                        c.contextualSub(
                            at[f"{locale}:consonant.init"],
                            c.input(
                                c.glyphClass([at[f"{locale}:o"], at[f"{locale}:u"]]),
                                self.conditions[f"{locale}:marked"],
                            ),
                        )

        if "MNG" in self.locales:
            with c.Lookup(
                "III.eac.o_u_oe_ue.marked", feature="rclt", flags={"UseMarkFilteringSet": at["fvs"]}
            ):
                variants = c.glyphClass(
                    at[f"MNG:{letter}.{position}"]
                    for letter in ["o", "u", "oe", "ue"]
                    for position in ["medi", "fina"]
                )
                c.contextualSub(
                    c.input(variants, self.conditions["MNG:default"]),
                    at["fvs"],
                )
                c.contextualSub(
                    at["fvs"],
                    c.input(variants, self.conditions["MNG:default"]),
                )

        # III.3: Phonetic - Particle
        # III.4: Graphemic - Devsger
        # III.5: Graphemic - Post bowed
        # III.6: Uncaptured - FVS

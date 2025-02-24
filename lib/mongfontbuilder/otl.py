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
        self.classes = {}
        self.conditions = {}

        self.initVariantClasses()
        self.initVariantConditions()
        self.initControlClassesAndConditions()

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

    def initControlClassesAndConditions(self):
        """
        Initialize glyph classes and condition lookups for control characters.

        For FVSes, `@fvs.ignored` indicates the state that needs to be ignored before FVS lookup, `@fvs.valid` indicates the state that is successfully matched after FVS lookup, and `@fvs.invalid` indicates the state that is not matched after FVS lookup.

        For MVS, `@mvs.valid` indicates the state that is successfully matched after chachlag or particle lookups, and `@mvs.invalid` indicates the state that is not matched after chachalg and particle lookups.

        For nirugu, `nirugu.ignored` indicates the nirugu as a `mark` that needs to be ignored, and `nirugu` indicate the valid nirugu as a `base`.
        """

        fvses = [f"fvs{i}" for i in range(1, 5)]
        for fvs in fvses:
            self.classes[fvs] = self.namedGlyphClass(fvs, [fvs, fvs + ".valid", fvs + ".ignored"])
        for name, items in {
            "mvs": ["mvs", "mvs.narrow", "mvs.wide", "nnbsp"],
            "mvs.invalid": ["mvs", "nnbsp"],
            "mvs.valid": ["mvs.narrow", "mvs.wide"],
            "fvs.invalid": fvses,
            "fvs.valid": [i + ".valid" for i in fvses],
            "fvs.ignored": [i + ".ignored" for i in fvses],
            "fvs": [self.classes[i] for i in fvses],
        }.items():
            self.classes[name] = self.namedGlyphClass(name, items)

        with self.Lookup("_.ignored") as _ignored:
            self.sub("nirugu", by="nirugu.ignored")
            self.sub("zwj", by="zwj.ignored")
            self.sub("zwnj", by="zwnj.ignored")

            if {"TOD", "TODx"}.intersection(self.locales):
                self.sub(self.classes["TOD:lvs"], by="lvs.ignored")

            for fvs in fvses:
                for suffix in ["", ".valid"]:
                    self.sub(f"{fvs}{suffix}", by=f"{fvs}.ignored")

        with self.Lookup("_.valid") as _valid:
            for fvs in fvses:
                for suffix in ["", ".ignored"]:
                    self.sub(f"{fvs}{suffix}", by=f"{fvs}.valid")

        with self.Lookup("_.invalid") as _invalid:
            for mvs in ["mvs.narrow", "mvs.wide"]:
                self.sub(mvs, by="mvs")
            self.sub("nirugu.ignored", by="nirugu")
            for fvs in fvses:
                for suffix in ["ignored", "valid"]:
                    self.sub(f"{fvs}.{suffix}", by=fvs)

        with self.Lookup("_.narrow") as _narrow:
            for mvs in ["mvs", "mvs.wide", "nnbsp"]:
                self.sub(mvs, by="mvs.narrow")

        with self.Lookup("_.wide") as _wide:
            for mvs in ["mvs", "mvs.narrow", "nnbsp"]:
                self.sub(mvs, by="mvs.wide")

        for lookup in [_ignored, _valid, _invalid, _narrow, _wide]:
            self.conditions[lookup.name] = lookup

    def initVariantClasses(self) -> None:
        """
        Initialize glyph classes for variants.

        `positionalClass` -- locale + ":" + alias + "." + position, e.g. `@MNG:a.isol`.

        `letterClass` -- locale + ":" + alias, e.g. `@MNG:a`.

        `categoryClass` -- locale + ":" + category (+ "." + position), e.g. `@MNG:vowel` or `@MNG:vowel.init`.
        """

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
                    self.classes[letter + "." + position] = positionalClass
                    positionalClasses.append(positionalClass)
                    categoryToClasses.setdefault(
                        locale + ":" + genderNeutralCategory + "." + position, []
                    ).append(positionalClass)

                letterClass = self.namedGlyphClass(letter, positionalClasses)
                self.classes[letter] = letterClass
                if genderNeutralCategory != category:
                    categoryToClasses.setdefault(locale + ":" + genderNeutralCategory, []).append(
                        letterClass
                    )
                categoryToClasses.setdefault(locale + ":" + category, []).append(letterClass)

            for name, positionalClasses in categoryToClasses.items():
                self.classes[name] = self.namedGlyphClass(name, positionalClasses)

    def initVariantConditions(self) -> None:
        """
        Initialize condition lookups for variants.

        condition generated from `variant.locales` -- locale + ":" + condition, e.g. `MNG:chachlag`.

        condition generated from `variant.default` -- locale + ":default", e.g. `MNG:default`.
        """

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
                self.conditions[lookup.name] = lookup

            if locale in ["MNG", "TOD", "TODx"]:
                with self.Lookup(f"{locale}:default") as lookup:
                    for position in joiningPositions:
                        for alias in getAliasesByLocale(locale):
                            charName = getCharNameByAlias(locale, alias)
                            self.sub(
                                self.classes[locale + ":" + alias + "." + position],
                                by=str(GlyphDescriptor.fromData(charName, position)),
                            )
                self.conditions[lookup.name] = lookup

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
        gc = self.classes
        cd = self.conditions

        with c.Lookup("III.controls.preprocessing", feature="rclt"):
            c.contextualSub(c.input("mvs", cd["_.invalid"]))
            c.contextualSub(
                c.input(c.glyphClass(["zwnj", "zwj", "nirugu", gc["fvs"]]), cd["_.ignored"])
            )

        for locale in ["TOD", "TODx"]:
            if locale in self.locales:
                with c.Lookup(
                    f"III.{locale}.lvs.preprocessing", feature="rclt", flags={"IgnoreMarks": True}
                ):
                    c.contextualSub(
                        c.input(
                            c.glyphClass(
                                [gc[f"{locale}:consonant.medi"], gc[f"{locale}:vowel.medi"]]
                            ),
                            cd[f"{locale}:default"],
                        ),
                        c.input(gc[f"{locale}:lvs.fina"], cd["_.ignored"]),
                    )
                    c.contextualSub(c.input(gc[f"{locale}:lvs"], cd["_.ignored"]))

        ### [III.1] Phonetic - Chachlag

        if "MNG" in self.locales:
            with c.Lookup("III.MNG.a_e.chachlag", feature="rclt", flags={"IgnoreMarks": True}):
                c.contextualSub(
                    c.input(gc["mvs"], cd["_.narrow"]),
                    c.input(c.glyphClass([gc["MNG:a.isol"], gc["MNG:e.isol"]]), cd["MNG:chachlag"]),
                )

            with c.Lookup(
                "III.eac.a_e.chachlag", feature="rclt", flags={"UseMarkFilteringSet": gc["fvs"]}
            ):
                c.contextualSub(
                    c.input(gc["mvs"], cd["_.invalid"]),
                    c.glyphClass([gc["MNG:a.isol"], gc["MNG:e.isol"]]),
                    gc["fvs"],
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
                        gc["MNG:consonant.init"],
                        c.input(
                            c.glyphClass([gc["MNG:o"], gc["MNG:u"], gc["MNG:oe"], gc["MNG:ue"]]),
                            cd["MNG:marked"],
                        ),
                    )
                if "MNGx" in self.locales:
                    c.contextualSub(
                        gc["MNGx:consonant.init"],
                        c.input(c.glyphClass([gc["MNGx:o"], gc["MNGx:ue"]]), cd["MNGx:marked"]),
                    )
                    c.contextualSub(
                        gc["MNGx:consonant.init"],
                        gc["MNGx:hX"],
                        c.input(gc["MNGx:ue"], cd["MNGx:marked"]),
                    )
                for locale in ["SIB", "MCH", "MCHx"]:
                    if locale in self.locales:
                        c.contextualSub(
                            gc[f"{locale}:consonant.init"],
                            c.input(
                                c.glyphClass([gc[f"{locale}:o"], gc[f"{locale}:u"]]),
                                cd[f"{locale}:marked"],
                            ),
                        )

        if "MNG" in self.locales:
            with c.Lookup(
                "III.eac.o_u_oe_ue.marked", feature="rclt", flags={"UseMarkFilteringSet": gc["fvs"]}
            ):
                variants = c.glyphClass(
                    gc[f"MNG:{letter}.{position}"]
                    for letter in ["o", "u", "oe", "ue"]
                    for position in ["medi", "fina"]
                )
                c.contextualSub(c.input(variants, cd["MNG:default"]), gc["fvs"])
                c.contextualSub(gc["fvs"], c.input(variants, cd["MNG:default"]))

        # III.3: Phonetic - Particle
        # III.4: Graphemic - Devsger
        # III.5: Graphemic - Post bowed
        # III.6: Uncaptured - FVS

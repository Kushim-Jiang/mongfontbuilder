import re
from dataclasses import dataclass
from typing import cast

from fontTools import unicodedata
from fontTools.feaLib import ast
from tptq.feacomposer import FeaComposer

from . import GlyphDescriptor, data, uNameFromCodePoint
from .data.misc import JoiningPosition, joiningPositions
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

        with self.Lookup("_.reset") as _reset:
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

        for lookup in [_ignored, _valid, _reset, _narrow, _wide]:
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

        Conditions generated from `variant.locales` -- locale + ":" + condition, e.g. `MNG:chachlag`.

        In addition, GB shaping requirements result in the need to reset the letter to its default variant. Resetting condition -- locale + ":reset", e.g. `MNG:reset`.
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

        if "MNG" in self.locales:
            with self.Lookup(f"MNG:reset") as lookup:
                for position in joiningPositions:
                    for alias in getAliasesByLocale("MNG"):
                        charName = getCharNameByAlias("MNG", alias)
                        self.sub(
                            self.classes["MNG:" + alias + "." + position],
                            by=str(GlyphDescriptor.fromData(charName, position)),
                        )
            self.conditions[lookup.name] = lookup

    def ia(self) -> None:
        """
        **Phase Ia: Basic character-to-glyph mapping**

        Since Unicode Version 16.0, NNBSP has been taken over by MVS, which participate in chachlag and particle shaping.
        """

        with self.Lookup("Ia.nnbsp.preprocessing", feature="ccmp"):
            self.sub("nnbsp", by="mvs")

    def iia(self) -> None:
        """
        **Phase IIa: Initiation of cursive positions**
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
        """
        **Phase III: Mongolian-specific shaping, reduction of phonetic letters to written units**
        """

        self.iii0()
        self.iii1()
        self.iii2()

        # III.3: Phonetic - Particle
        # III.4: Graphemic - Devsger
        # III.5: Graphemic - Post bowed
        # III.6: Uncaptured - FVS

    def iii0(self):
        """
        **Phase III.0: Control character preprocessing**
        """

        self.iii0a()
        if "MNG" in self.locales:
            self.iii0b()

    def iii0a(self):
        """
        Before Mongolian-specific shaping steps, ZWNJ, ZWJ, nirugu, Todo (Ali Gali) long vowel sign and FVS need to be substituted to ignored glyphs, while MVS needs to be substituted to invalid glyph.

        Specifically, for Todo (Ali Gali) long vowel sign, when the final long vowel sign is substituted to ignored glyph, the joining position of the previous letter will be changed (from `init` to `isol`, from `medi` to `fina`).
        """

        c = self
        cl = self.classes
        cd = self.conditions

        with c.Lookup("III.controls.preprocessing", feature="rclt"):
            c.contextualSub(c.input("mvs", cd["_.reset"]))
            c.contextualSub(
                c.input(c.glyphClass(["zwnj", "zwj", "nirugu", cl["fvs"]]), cd["_.ignored"])
            )

        for locale in ["TOD", "TODx"]:
            if locale in self.locales:
                with self.Lookup(f"{locale}:lvs.preprocessing") as lvsPreprocessing:
                    positions: list[tuple[JoiningPosition, JoiningPosition]] = [
                        ("init", "isol"),
                        ("medi", "fina"),
                    ]
                    for position1, position2 in positions:
                        for alias in getAliasesByLocale(locale):
                            charName = getCharNameByAlias(locale, alias)
                            self.sub(
                                str(GlyphDescriptor.fromData(charName, position1)),
                                by=str(GlyphDescriptor.fromData(charName, position2)),
                            )

                with c.Lookup(
                    f"III.{locale}.lvs.preprocessing", feature="rclt", flags={"IgnoreMarks": True}
                ):
                    variants = c.glyphClass(
                        [
                            cl[f"{locale}:consonant.init"],
                            cl[f"{locale}:vowel.init"],
                            cl[f"{locale}:consonant.medi"],
                            cl[f"{locale}:vowel.medi"],
                        ]
                    )
                    c.contextualSub(
                        c.input(variants, lvsPreprocessing),
                        c.input(cl[f"{locale}:lvs.fina"], cd["_.ignored"]),
                    )
                    c.contextualSub(c.input(cl[f"{locale}:lvs"], cd["_.ignored"]))

    def iii0b(self):
        """
        GB requires that the masculinity and femininity of a letter be passed forward and backward indefinitely throughout the word.

        A to C implement masculinity indefinitely passing forward, D to F implement femininity indefinitely passing forward, G to K implement masculinity indefinitely passing backward.
        """

        c = self
        cl = self.classes
        ct = data.locales["MNG"].categories

        init = cast(JoiningPosition, "init")
        medi = cast(JoiningPosition, "medi")
        fina = cast(JoiningPosition, "fina")

        masculine = c.glyphClass(["masculine"])
        feminine = c.glyphClass(["feminine"])

        def getDefault(alias: str, position: JoiningPosition, marked: bool = False) -> str:
            charName = getCharNameByAlias("MNG", alias)
            return str(
                GlyphDescriptor.fromData(
                    charName, position, suffixes=(["marked"] if marked else [])
                )
            )

        # add masculine
        with c.Lookup("III.ig.preprocessing.A", feature="rclt"):
            for alias in ct["vowelMasculine"]:
                for position in (init, medi):
                    default = getDefault(alias, position)
                    self.sub(default, by=[default, "masculine"])

        with c.Lookup(
            "III.ig.preprocessing.B", feature="rclt", flags={"UseMarkFilteringSet": masculine}
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (medi, fina):
                    default = getDefault(alias, position)
                    self.contextualSub(
                        "masculine", c.input(default), by=" ".join([default, "masculine"])
                    )  # FIXME: treat as glyph name

        with c.Lookup("III.ig.preprocessing.C", feature="rclt"):
            for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]:
                if alias not in ["g", "h"]:
                    for position in (init, medi, fina):
                        default = getDefault(alias, position)
                        self.sub(default, "masculine", by=default)

        # add feminine
        with c.Lookup("III.ig.preprocessing.D", feature="rclt"):
            for alias in ct["vowelFeminine"]:
                for position in (init, medi):
                    default = getDefault(alias, position)
                    self.sub(default, by=[default, "feminine"])

        with c.Lookup(
            "III.ig.preprocessing.E", feature="rclt", flags={"UseMarkFilteringSet": feminine}
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (medi, fina):
                    default = getDefault(alias, position)
                    self.contextualSub(
                        "feminine", c.input(default), by=" ".join([default, "feminine"])
                    )  # FIXME: treat as glyph name

        with c.Lookup("III.ig.preprocessing.F", feature="rclt"):
            for alias in ct["vowelFeminine"] + ct["vowelNeuter"] + ct["consonant"]:
                if alias not in ["g", "h"]:
                    for position in (init, medi, fina):
                        default = getDefault(alias, position)
                        self.sub(default, "feminine", by=default)

        # reverse add masculine
        unmarkedVariants = c.namedGlyphClass(
            "MNG:unmarked.A",
            [
                getDefault(alias, position)
                for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                for position in (init, medi, fina)
            ],
        )
        markedVariants = c.namedGlyphClass(
            "MNG:marked.A",
            [
                getDefault(alias, position, True)
                for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                for position in (init, medi, fina)
            ],
        )

        with c.Lookup("_.marked.MNG") as _marked:
            self.sub(unmarkedVariants, by=markedVariants)

        with c.Lookup("_.unmarked.MNG") as _unmarked:
            self.sub(markedVariants, by=unmarkedVariants)

        with c.Lookup("III.ig.preprocessing.G", feature="rclt", flags={"IgnoreMarks": True}):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (init, medi):
                    unmarked = getDefault(alias, position)
                    self.contextualSub(c.input(unmarked, _marked), cl["MNG:vowelMasculine"])
            for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]:
                unmarked = getDefault(alias, fina)
                self.contextualSub(c.input(unmarked, _marked), cl["mvs"], cl["MNG:a.isol"])

        with c.Lookup(
            "III.ig.preprocessing.H", feature="rclt", flags={"UseMarkFilteringSet": feminine}
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (init, medi):
                    unmarked = getDefault(alias, position)
                    marked = getDefault(alias, position, True)
                    self.current.append(
                        ast.ReverseChainSingleSubstStatement(
                            old_prefix=[],
                            old_suffix=["@" + markedVariants.name],  # FIXME: treat as glyph name
                            glyphs=[unmarked],
                            replacements=[marked],
                        )
                    )

        with c.Lookup("III.ig.preprocessing.I", feature="rclt"):
            for alias in ["g", "h"]:
                for position in (init, medi):
                    marked = getDefault(alias, position, True)
                    self.contextualSub(c.input(marked, _unmarked), "masculine")

        with c.Lookup("III.ig.preprocessing.J", feature="rclt"):
            markedVariants = c.namedGlyphClass(
                "MNG:marked.B",
                [
                    getDefault(alias, position, True)
                    for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                    if alias not in ["h", "g"]
                    for position in (init, medi, fina)
                ],
            )
            self.contextualSub(c.input(markedVariants, _unmarked))

        with c.Lookup("III.ig.preprocessing.K", feature="rclt"):
            for alias in ["h", "g"]:
                for position in (init, medi):
                    unmarked = getDefault(alias, position)
                    marked = getDefault(alias, position, True)
                    self.sub(marked, by=[unmarked, "masculine"])

    def iii1(self):
        """
        **Phase III.1: Phonetic - Chachlag**

        The isolated Hudum _a_, _e_ and Hudum Ali Gali _a_ (same as Hudum _a_) choose `Aa` when follow an MVS, while MVS chooses the narrow space glyph.

        According to GB, when Hudum _a_ and _e_ are followed by FVS, the MVS shaping needs to be postponed to particle lookup, so MVS needs to be reset at this time. For example, for <MVS, _a_, FVS2>, in this step should be invalid MVS, isolated default _a_ and ignored FVS2. Since the function of NNBSP is transferred to MVS, this step, although required by GB, is essential, so the lookup name does not have a GB suffix.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        if "MNG" in self.locales:
            with c.Lookup("III.a_e.chachlag.A", feature="rclt", flags={"IgnoreMarks": True}):
                c.contextualSub(
                    c.input(cl["mvs"], cd["_.narrow"]),
                    c.input(c.glyphClass([cl["MNG:a.isol"], cl["MNG:e.isol"]]), cd["MNG:chachlag"]),
                )

            with c.Lookup(
                "III.a_e.chachlag.B", feature="rclt", flags={"UseMarkFilteringSet": cl["fvs"]}
            ):
                c.contextualSub(
                    c.input(cl["mvs"], cd["_.reset"]),
                    c.glyphClass([cl["MNG:a.isol"], cl["MNG:e.isol"]]),
                    cl["fvs"],
                )

    def iii2(self):

        c = self
        cl = self.classes
        cd = self.conditions

        # III.2: Phonetic - Syllabic

        if {"MNG", "MNGx", "MCH", "MCHx", "SIB"}.intersection(self.locales):
            with c.Lookup(
                "III.o_u_oe_ue.marked",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                if "MNG" in self.locales:
                    c.contextualSub(
                        cl["MNG:consonant.init"],
                        c.input(
                            c.glyphClass([cl["MNG:o"], cl["MNG:u"], cl["MNG:oe"], cl["MNG:ue"]]),
                            cd["MNG:marked"],
                        ),
                    )
                if "MNGx" in self.locales:
                    c.contextualSub(
                        cl["MNGx:consonant.init"],
                        c.input(c.glyphClass([cl["MNGx:o"], cl["MNGx:ue"]]), cd["MNGx:marked"]),
                    )
                    c.contextualSub(
                        cl["MNGx:consonant.init"],
                        cl["MNGx:hX"],
                        c.input(cl["MNGx:ue"], cd["MNGx:marked"]),
                    )
                for locale in ["SIB", "MCH", "MCHx"]:
                    if locale in self.locales:
                        c.contextualSub(
                            cl[f"{locale}:consonant.init"],
                            c.input(
                                c.glyphClass([cl[f"{locale}:o"], cl[f"{locale}:u"]]),
                                cd[f"{locale}:marked"],
                            ),
                        )

        if "MNG" in self.locales:
            with c.Lookup(
                "III.o_u_oe_ue.marked.GB.A",
                feature="rclt",
                flags={"UseMarkFilteringSet": cl["fvs"]},
            ):
                variants = c.glyphClass(
                    cl[f"MNG:{letter}.{position}"]
                    for letter in ["o", "u", "oe", "ue"]
                    for position in ["medi", "fina"]
                )
                c.contextualSub(c.input(variants, cd["MNG:reset"]), cl["fvs"])
                c.contextualSub(cl["fvs"], c.input(variants, cd["MNG:reset"]))

        # TODO

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

    def getDefault(self, alias: str, position: JoiningPosition | str, marked: bool = False) -> str:
        charName = getCharNameByAlias("MNG", alias)
        position = cast(JoiningPosition, position)
        return str(
            GlyphDescriptor.fromData(charName, position, suffixes=(["marked"] if marked else []))
        )

    def iii0b(self):
        """
        GB requires that the masculinity and femininity of a letter be passed forward and backward indefinitely throughout the word.

        A to C implement masculinity indefinitely passing forward, D to F implement femininity indefinitely passing forward, G to K implement masculinity indefinitely passing backward.
        """

        c = self
        cl = self.classes
        cd = self.conditions
        ct = data.locales["MNG"].categories

        masculine = c.glyphClass(["masculine"])
        feminine = c.glyphClass(["feminine"])

        # add masculine
        with c.Lookup("III.ig.preprocessing.A", feature="rclt"):
            for alias in ct["vowelMasculine"]:
                for position in ["init", "medi"]:
                    default = self.getDefault(alias, position)
                    self.sub(default, by=[default, "masculine"])

        with c.Lookup(
            "III.ig.preprocessing.B", feature="rclt", flags={"UseMarkFilteringSet": masculine}
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in ["medi", "fina"]:
                    default = self.getDefault(alias, position)
                    self.contextualSub(
                        "masculine", c.input(default), by=" ".join([default, "masculine"])
                    )  # FIXME: treat as glyph name

        with c.Lookup("III.ig.preprocessing.C", feature="rclt"):
            for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]:
                if alias not in ["g", "h"]:
                    for position in ["init", "medi", "fina"]:
                        default = self.getDefault(alias, position)
                        self.sub(default, "masculine", by=default)

        # add feminine
        with c.Lookup("III.ig.preprocessing.D", feature="rclt"):
            for alias in ct["vowelFeminine"]:
                for position in ["init", "medi"]:
                    default = self.getDefault(alias, position)
                    self.sub(default, by=[default, "feminine"])

        with c.Lookup(
            "III.ig.preprocessing.E", feature="rclt", flags={"UseMarkFilteringSet": feminine}
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in ["medi", "fina"]:
                    default = self.getDefault(alias, position)
                    self.contextualSub(
                        "feminine", c.input(default), by=" ".join([default, "feminine"])
                    )  # FIXME: treat as glyph name

        with c.Lookup("III.ig.preprocessing.F", feature="rclt"):
            for alias in ct["vowelFeminine"] + ct["vowelNeuter"] + ct["consonant"]:
                if alias not in ["g", "h"]:
                    for position in ["init", "medi", "fina"]:
                        default = self.getDefault(alias, position)
                        self.sub(default, "feminine", by=default)

        # reverse add masculine
        unmarkedVariants = c.namedGlyphClass(
            "MNG:unmarked.A",
            [
                self.getDefault(alias, position)
                for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                for position in ["init", "medi", "fina"]
            ],
        )
        markedVariants = c.namedGlyphClass(
            "MNG:marked.A",
            [
                self.getDefault(alias, position, True)
                for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                for position in ["init", "medi", "fina"]
            ],
        )

        with c.Lookup("_.marked.MNG") as _marked:
            self.sub(unmarkedVariants, by=markedVariants)
        cd[_marked.name] = _marked

        with c.Lookup("_.unmarked.MNG") as _unmarked:
            self.sub(markedVariants, by=unmarkedVariants)
        cd[_unmarked.name] = _unmarked

        with c.Lookup("III.ig.preprocessing.G", feature="rclt", flags={"IgnoreMarks": True}):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in ["init", "medi"]:
                    unmarked = self.getDefault(alias, position)
                    self.contextualSub(c.input(unmarked, _marked), cl["MNG:vowelMasculine"])
            for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]:
                unmarked = self.getDefault(alias, "fina")
                self.contextualSub(c.input(unmarked, _marked), cl["mvs"], cl["MNG:a.isol"])

        with c.Lookup(
            "III.ig.preprocessing.H", feature="rclt", flags={"UseMarkFilteringSet": feminine}
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in ["init", "medi"]:
                    unmarked = self.getDefault(alias, position)
                    marked = self.getDefault(alias, position, True)
                    self.current.append(
                        ast.ReverseChainSingleSubstStatement(
                            old_prefix=[],
                            old_suffix=["@" + markedVariants.name],
                            glyphs=[unmarked],
                            replacements=[marked],
                        )
                    )

        with c.Lookup("III.ig.preprocessing.I", feature="rclt"):
            for alias in ["g", "h"]:
                for position in ["init", "medi"]:
                    marked = self.getDefault(alias, position, True)
                    self.contextualSub(c.input(marked, _unmarked), "masculine")

        with c.Lookup("III.ig.preprocessing.J", feature="rclt"):
            markedVariants = c.namedGlyphClass(
                "MNG:marked.B",
                [
                    self.getDefault(alias, position, True)
                    for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                    if alias not in ["h", "g"]
                    for position in ["init", "medi", "fina"]
                ],
            )
            self.contextualSub(c.input(markedVariants, _unmarked))

        with c.Lookup("III.ig.preprocessing.K", feature="rclt"):
            for alias in ["h", "g"]:
                for position in ["init", "medi"]:
                    unmarked = self.getDefault(alias, position)
                    marked = self.getDefault(alias, position, True)
                    self.sub(marked, by=[unmarked, "masculine"])

    def iii1(self):
        """
        **Phase III.1: Phonetic - Chachlag**

        The isolated Hudum _a_, _e_ and Hudum Ali Gali _a_ (same as Hudum _a_) choose `Aa` when follow an MVS, while MVS chooses the narrow space glyph.

        According to GB, when Hudum _a_ and _e_ are followed by FVS, the MVS shaping needs to be postponed to particle lookup, so MVS needs to be reset at this time. For example, for an MVS, an _a_ and an FVS2, in this step should be invalid MVS, isolated default _a_ and ignored FVS2. Since the function of NNBSP is transferred to MVS, this step, although required by GB, is essential, so the lookup name does not have a GB suffix.
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
        """
        **Phase III.2: Phonetic - Syllabic**
        """

        self.iii2a()
        self.iii2b()
        self.iii2c()
        self.iii2d()
        self.iii2e()

    def iii2a(self):
        """
        (1) When Hudum _o_ or _u_ or _oe_ or _ue_ follows an initial consonant, apply `marked`.

        According to GB requirements: The `marked` will be skipped if the vowel precedes or follows an FVS, although Hudum _g_ or _h_ with FVS2 or FVS4 will apply `marked` for _oe_ or _ue_; when the first syllable contains a consonant cluster, the `marked` will still be applied.

        (2) When initial Hudum _d_ follows a final vowel, apply `marked`. Appear in Twelve Syllabaries.

        According to GB requirements: The `marked` will be skipped if the vowel precedes or follows an FVS.
        """

        c = self
        cl = self.classes
        cd = self.conditions
        ct = data.locales["MNG"].categories

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

            with c.Lookup(
                "III.o_u_oe_ue.marked.GB.B",
                feature="rclt",
                flags={"UseMarkFilteringSet": cl["fvs"]},
            ):
                c.contextualSub(
                    c.glyphClass([cl["MNG:g.init"], cl["MNG:h.init"]]),
                    c.glyphClass([cl["fvs2"], cl["fvs4"]]),
                    c.input(c.glyphClass([cl["MNG:oe.fina"], cl["MNG:ue.fina"]]), cd["MNG:marked"]),
                )

            markedVariants = c.namedGlyphClass(
                "MNG:marked.C",
                [
                    self.getDefault(alias, position, True)
                    for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                    for position in ["init", "medi", "fina"]
                ],
            )
            with c.Lookup(
                "III.o_u_oe_ue.initial_marked.GB.A", feature="rclt", flags={"IgnoreMarks": True}
            ):
                c.contextualSub(
                    c.glyphClass([cl["MNG:consonant.init"], markedVariants]),
                    c.input(cl["MNG:consonant.medi"], cd["_.marked.MNG"]),
                )

            variants = c.glyphClass(cl[f"MNG:{letter}.medi"] for letter in ["o", "u", "oe", "ue"])
            with c.Lookup(
                "III.o_u_oe_ue.initial_marked.GB.B", feature="rclt", flags={"IgnoreMarks": True}
            ):
                c.contextualSub(
                    c.glyphClass([cl["MNG:consonant.init"], markedVariants]),
                    c.input(variants, cd["MNG:marked"]),
                )

            with c.Lookup("III.o_u_oe_ue.initial_marked.GB.C", feature="rclt"):
                c.contextualSub(c.input(markedVariants, cd["_.unmarked.MNG"]))

            with c.Lookup("III.d.marked", feature="rclt", flags={"IgnoreMarks": True}):
                c.contextualSub(c.input(cl["MNG:d.init"], cd["MNG:marked"]), cl["MNG:vowel.fina"])

            with c.Lookup(
                "III.d.marked.GB", feature="rclt", flags={"UseMarkFilteringSet": cl["fvs"]}
            ):
                c.contextualSub(
                    c.input(cl["MNG:d.init"], cd["MNG:reset"]), cl["MNG:vowel.fina"], cl["fvs"]
                )
                c.contextualSub(
                    c.input(cl["MNG:d.init"], cd["MNG:reset"]), cl["fvs"], cl["MNG:vowel.fina"]
                )

    def iii2b(self):
        """
        (1) When Sibe _z_ precedes _i_, apply `marked`.

        (2) When Manchu _i_ follows _z_, apply `marked`.

        (3) When Manchu _f_ precedes _i_ or _o_ or _u_ or _ue_, apply `marked`.

        (4) When Manchu Ali Gali _i_ follows _cX_ or _z_ or _jhX_, apply `marked`.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        if {"SIB", "MCH", "MCHx"}.intersection(self.locales):
            with c.Lookup(
                "III.z_f_i.marked.SIB_MCH_MCHx", feature="rclt", flags={"IgnoreMarks": True}
            ):
                if "SIB" in self.locales:
                    c.contextualSub(c.input(cl["SIB:z"], cd["SIB:marked"]), cl["SIB:i"])
                if "MCH" in self.locales:
                    c.contextualSub(cl["MCH:z"], c.input(cl["MCH:i"], cd["MCH:marked"]))
                    c.contextualSub(
                        c.input(cl["MCH:f"], cd["MCH:marked"]),
                        c.glyphClass([cl["MCH:i"], cl["MCH:o"], cl["MCH:u"], cl["MCH:ue"]]),
                    )
                if "MCHx" in self.locales:
                    c.contextualSub(
                        c.glyphClass([cl["MCHx:cX"], cl["MCHx:z"], cl["MCHx:jhX"]]),
                        c.input(cl["MCHx:i"], cd["MCHx:marked"]),
                    )

    def iii2c(self):
        """
        When Hudum _n_, _j_, _w_  follows an MVS that follows chachlag _a_ or _e_, apply `chachlag_onset`. When Hudum _h_, _g_, Hudum Ali Gali _a_ follows an MVS that follows chachlag _a_, apply `chachlag_onset`.

        According to GB requirements, when Hudum _g_ follows an MVS that follows chachlag _e_, apply `chachlag_devsger`.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        if {"MNG", "MNGx"}.intersection(self.locales):
            with c.Lookup(
                "III.n_j_w_h_g_a.chachlag_onset.MNG_MNGx",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                njwVariants = c.glyphClass(
                    [cl["MNG:n.fina"], cl["MNG:j.isol"], cl["MNG:j.fina"], cl["MNG:w.fina"]]
                )
                hgVariants = c.glyphClass([cl["MNG:h.fina"], cl["MNG:g.fina"]])
                if "MNG" in self.locales:
                    c.contextualSub(
                        c.input(njwVariants, cd["MNG:chachlag_onset"]),
                        cl["mvs.valid"],
                        c.glyphClass(["u1820.Aa.isol", "u1821.Aa.isol"]),
                    )
                    c.contextualSub(
                        c.input(hgVariants, cd["MNG:chachlag_onset"]),
                        cl["mvs.valid"],
                        "u1820.Aa.isol",
                    )
                if "MNGx" in self.locales:
                    c.contextualSub(
                        c.input(cl["MNGx:a.fina"], cd["MNG:chachlag_onset"]),
                        cl["mvs.valid"],
                        "u1820.Aa.isol",
                    )

        if "MNG" in self.locales:
            with c.Lookup(
                "III.g.chachlag_onset.MNG.GB", feature="rclt", flags={"IgnoreMarks": True}
            ):
                c.contextualSub(
                    c.input(cl["MNG:g.fina"], cd["MNG:chachlag_onset_gb"]),
                    cl["mvs.valid"],
                    "u1821.Aa.isol",
                )

    def iii2d(self):
        """
        (1) When Sibe _e_ or _u_ follows _t_, _d_, _k_, _g_, _h_, apply `feminine`.

        (2) When Manchu _e_, _u_ follows _t_, _d_, _k_, _g_, _h_, apply `feminine`.

        (3) When Manchu Ali Gali _e_, _u_ follows _tX_, _t_, _d_, _dhX_, _g_, _k_, _ghX_, _h_, apply `feminine`. When Manchu Ali Gali _e_ follows _ngX_, _sbm_, apply `feminine`.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        if {"SIB", "MCH", "MCHx"}.intersection(self.locales):
            with c.Lookup(
                "III.e_u.feminine.SIB_MCH_MCHx", feature="rclt", flags={"IgnoreMarks": True}
            ):
                for locale in ["SIB", "MCH", "MCHx"]:
                    if locale in self.locales:
                        consonants = c.glyphClass(
                            cl[f"{locale}:{letter}"] for letter in ["t", "d", "k", "g", "h"]
                        )
                        if locale == "MCHx":
                            consonants = c.glyphClass(
                                cl[f"MCHx:{letter}"]
                                for letter in ["tX", "t", "d", "dhX", "g", "k", "ghX", "h"]
                            )
                        euLetters = c.glyphClass([cl[f"{locale}:e"], cl[f"{locale}:u"]])
                        c.contextualSub(
                            consonants, c.input("u1860.Oh.fina", cd[f"{locale}:feminine_marked"])
                        )
                        c.contextualSub(consonants, c.input(euLetters, cd[f"{locale}:feminine"]))

                        if locale == "MCHx":
                            c.contextualSub(
                                c.glyphClass([cl["MCHx:ngX"], cl["MCHx:sbm"]]),
                                c.input(euLetters, cd["MCHx:feminine"]),
                            )

    def iii2e(self):
        """
        (1) For Hudum, Todo, Sibe, Manchu and Manchu Ali Gali, when _n_ follows a vowel, apply `onset`; when _n_ follows a consonant, apply `devsger`.

        (2) For Hudum, When _t_ or _d_ follows a vowel, apply `onset`; when _t_ or _d_ follows a consonant, apply `devsger`. For Sibe and Manchu, when _t_ or _d_ follows _a_ or _i_ or _o_, apply `masculine_onset`; when _t_ or _d_ follows _e_, _u_, _ue_, apply `feminine`; when _t_ follows a consonant, apply `devsger`; when _t_ precedes a vowel, apply `devsger`. For Manchu Ali Gali, when _tX_ or _dhX_ follows _a_ or _i_ or _o_, apply `masculine_onset`; when _tX_ or _dhX_ follows _e_ or _u_ or _ue_, apply `feminine`.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        if {"MNG", "TOD", "SIB", "MCH", "MCHx"}.intersection(self.locales):
            with c.Lookup(
                "III.n.onset_and_devsger.MNG_TOD_SIB_MCH_MCHx",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                for locale in ["MNG", "TOD", "SIB", "MCH", "MCHx"]:
                    if locale in self.locales:
                        c.contextualSub(
                            c.input(cl[f"{locale}:n"], cd[f"{locale}:onset"]), cl[f"{locale}:vowel"]
                        )
                        c.contextualSub(
                            c.input(cl[f"{locale}:n"], cd[f"{locale}:devsger"]),
                            cl[f"{locale}:consonant"],
                        )

        if {"MNG", "SIB", "MCH", "MCHx"}.intersection(self.locales):
            with c.Lookup(
                "III.t_d.onset_and_devsger_and_gender.MNG_MCH_MCHx",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                if "MNG" in self.locales:
                    # FIXME: ignore sub [@t-hud.init @d-hud.init]' @hud.vowel.fina;
                    tdLetters = c.glyphClass(cl[f"MNG:{letter}"] for letter in ["t", "d"])
                    c.contextualSub(c.input(tdLetters, cd["MNG:onset"]), cl["MNG:vowel"])
                    c.contextualSub(c.input(tdLetters, cd["MNG:devsger"]), cl["MNG:consonant"])
                for locale in ["SIB", "MCH", "MCHx"]:
                    if locale in self.locales:
                        tdLetters = c.glyphClass(cl[f"{locale}:{i}"] for i in ["t", "d"])
                        if locale == "MCHx":
                            tdLetters = c.glyphClass(cl[f"MCHx:{i}"] for i in ["tX", "dhX"])
                        aioLetters = c.glyphClass(cl[f"{locale}:{i}"] for i in ["a", "i", "o"])
                        euueLetters = c.glyphClass(cl[f"{locale}:{i}"] for i in ["e", "u", "ue"])
                        c.contextualSub(
                            c.input(tdLetters, cd[f"{locale}:masculine_onset"]), aioLetters
                        )
                        c.contextualSub(c.input(tdLetters, cd[f"{locale}:feminine"]), euueLetters)
                        if locale != "MCHx":
                            c.contextualSub(
                                c.input(cl[f"{locale}:t"], cd[f"{locale}:devsger"]),
                                cl[f"{locale}:consonant"],
                            )
                            c.contextualSub(
                                cl[f"{locale}:vowel"],
                                c.input(cl[f"{locale}:t.fina"], cd[f"{locale}:devsger"]),
                            )

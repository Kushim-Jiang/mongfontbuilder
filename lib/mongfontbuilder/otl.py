import re
from dataclasses import dataclass
from typing import Iterable

from fontTools import unicodedata
from fontTools.feaLib import ast
from tptq.feacomposer import AnyGlyph, ContextualInput, FeaComposer, _NormalizedAnyGlyph

from . import GlyphDescriptor, data, uNameFromCodePoint
from .data.misc import JoiningPosition, fina, init, isol, joiningPositions, medi
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

        self.initControls()
        self.initVariants()

        self.ia()
        self.iia()
        self.iii()
        self.iib1()

        # TODO: IIb.2: cleanup of format controls
        # TODO: IIb.3: optional treatments

        # TODO: Ib: vertical punctuation
        # TODO: Ib: punctuation ligature
        # TODO: Ib: proportional punctuation
        # TODO: Ib: marks position

    def rsub(
        self, *glyphs: AnyGlyph | ContextualInput, by: AnyGlyph
    ) -> ast.ReverseChainSingleSubstStatement:
        prefix = list[_NormalizedAnyGlyph]()
        input = list[_NormalizedAnyGlyph]()
        suffix = list[_NormalizedAnyGlyph]()
        for item in glyphs:
            if isinstance(item, ContextualInput):
                assert not suffix, glyphs
                input.append(item.glyph)
            elif input:
                suffix.append(self._normalized(item))
            else:
                prefix.append(self._normalized(item))
        if not input:
            input = prefix
            prefix = []
        output = self._normalized(by)
        statement = ast.ReverseChainSingleSubstStatement(
            glyphs=input, replacements=[output], old_prefix=prefix, old_suffix=suffix
        )
        self.current.append(statement)
        return statement

    def initControls(self):
        """
        Initialize glyph classes and condition lookups for control characters.

        For FVSes, `@fvs.ignored` indicates the state that needs to be ignored before FVS lookup, `@fvs.valid` indicates the state that is successfully matched after FVS lookup, and `@fvs.invalid` indicates the state that is not matched after FVS lookup.

        For MVS, `@mvs.valid` indicates the state that is successfully matched after chachlag or particle lookups, and `@mvs.invalid` indicates the state that is not matched after chachlag and particle lookups.

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

    def initVariants(self) -> None:
        """
        Initialize glyph classes for variants.

        `positionalClass` -- locale + ":" + alias + "." + position, e.g. `@MNG:a.isol`.

        `letterClass` -- locale + ":" + alias, e.g. `@MNG:a`.

        `categoryClass` -- locale + ":" + category (+ "." + position), e.g. `@MNG:vowel` or `@MNG:vowel.init`.

        Initialize condition lookups for variants.

        Conditions generated from `variant.locales` -- locale + ":" + condition, e.g. `MNG:chachlag`.

        In addition, GB shaping requirements result in the need to reset the letter to its default variant. Resetting condition -- locale + ":reset", e.g. `MNG:reset`.
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

                if locale.startswith("TOD") and alias in data.locales[locale].categories["lvs"]:
                    lvsCharName = getCharNameByAlias(locale, "lvs")
                    letter += "_lvs"
                    lvsPositionalClasses = list[ast.GlyphClassDefinition]()
                    for charPosition in (init, medi):
                        charVariant = GlyphDescriptor.fromData(charName, charPosition)
                        for lvsPosition in (medi, fina):
                            lvsVariant = GlyphDescriptor.fromData(lvsCharName, lvsPosition)
                            charLvsVariant = charVariant + lvsVariant
                            positionalClass = self.namedGlyphClass(
                                letter + "." + charLvsVariant.position, [str(charLvsVariant)]
                            )
                            self.classes[letter + "." + charLvsVariant.position] = positionalClass
                            lvsPositionalClasses.append(positionalClass)
                    letterClass = self.namedGlyphClass(letter, lvsPositionalClasses)
                    self.classes[letter] = letterClass
                    if genderNeutralCategory != category:
                        categoryToClasses.setdefault(
                            locale + ":" + genderNeutralCategory, []
                        ).append(letterClass)
                    categoryToClasses.setdefault(locale + ":" + category, []).append(letterClass)

            for name, positionalClasses in categoryToClasses.items():
                self.classes[name] = self.namedGlyphClass(name, positionalClasses)

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

    def variants(
        self,
        locale: LocaleID,
        aliases: str | Iterable[str],
        positions: JoiningPosition | Iterable[JoiningPosition] | None = None,
        writtens: str | Iterable[str] | None = None,
    ) -> ast.GlyphClass:
        aliases = [aliases] if isinstance(aliases, str) else aliases
        positions = [positions] if isinstance(positions, str) else positions
        writtens = [writtens] if isinstance(writtens, str) else writtens
        if writtens and positions:
            codePoints = [
                ord(unicodedata.lookup(getCharNameByAlias(locale, alias))) for alias in aliases
            ]
            return self.glyphClass(
                str(GlyphDescriptor([codePoint], [written], position, []))
                for codePoint in codePoints
                for position in positions
                for written in writtens
            )
        return self.glyphClass(
            self.classes[f"{locale}:{alias}" + (f".{position}" if position else "")]
            for alias in aliases
            for position in positions or [None]
        )

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
        self.iii3()
        self.iii4()
        self.iii5()
        self.iii6()

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
            c.sub(c.input("mvs", cd["_.reset"]))
            c.sub(c.input(c.glyphClass(["zwnj", "zwj", "nirugu", cl["fvs"]]), cd["_.ignored"]))

        for locale in ["TOD", "TODx"]:
            if locale in self.locales:
                lvsCharName = getCharNameByAlias("TOD", "lvs")
                with c.Lookup(
                    f"III.lvs.preprocessing.{locale}", feature="rclt", flags={"IgnoreMarks": True}
                ):
                    for alias in data.locales[locale].categories["lvs"]:
                        charName = getCharNameByAlias(locale, alias)
                        for position in (init, medi):
                            charVar = GlyphDescriptor.fromData(charName, position)
                            for lvsPosition in (medi, fina):
                                lvsVar = GlyphDescriptor.fromData(lvsCharName, lvsPosition)
                                self.sub(str(charVar), str(lvsVar), by=str(charVar + lvsVar))

    def getDefault(self, alias: str, position: JoiningPosition, marked: bool = False) -> str:
        charName = getCharNameByAlias("MNG", alias)
        suffix = ["marked"] if marked else []
        return str(GlyphDescriptor.fromData(charName, position, suffixes=suffix))

    def iii0b(self):
        """
        GB requires that the masculinity and femininity of a letter be passed forward and backward indefinitely throughout the word.

        A to C implement masculinity indefinitely passing forward, D to F implement femininity indefinitely passing forward, G to K implement masculinity indefinitely passing backward.
        """

        c = self
        cl = self.classes
        cd = self.conditions
        ct = data.locales["MNG"].categories

        masc, femi = "masculine", "feminine"
        mascClass, femiClass = c.glyphClass([masc]), c.glyphClass([femi])

        # add masculine
        with c.Lookup("III.ig.preprocessing.A", feature="rclt"):
            for alias in ct["vowelMasculine"]:
                for position in (init, medi):
                    default = self.getDefault(alias, position)
                    self.sub(default, by=[default, masc])

        with c.Lookup(
            "III.ig.preprocessing.B", feature="rclt", flags={"UseMarkFilteringSet": mascClass}
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (medi, fina):
                    default = self.getDefault(alias, position)
                    self.sub(masc, c.input(default), by=[default, masc])

        with c.Lookup("III.ig.preprocessing.C", feature="rclt"):
            for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]:
                if alias not in ["h", "g"]:
                    for position in (init, medi, fina):
                        default = self.getDefault(alias, position)
                        self.sub(default, masc, by=default)

        # add feminine
        with c.Lookup("III.ig.preprocessing.D", feature="rclt"):
            for alias in ct["vowelFeminine"]:
                for position in (init, medi):
                    default = self.getDefault(alias, position)
                    self.sub(default, by=[default, femi])

        with c.Lookup(
            "III.ig.preprocessing.E", feature="rclt", flags={"UseMarkFilteringSet": femiClass}
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (medi, fina):
                    default = self.getDefault(alias, position)
                    self.sub(femi, c.input(default), by=[default, femi])

        with c.Lookup("III.ig.preprocessing.F", feature="rclt"):
            for alias in ct["vowelFeminine"] + ct["vowelNeuter"] + ct["consonant"]:
                if alias not in ["h", "g"]:
                    for position in (init, medi, fina):
                        default = self.getDefault(alias, position)
                        self.sub(default, femi, by=default)

        # reverse add masculine
        unmarkedVariants = c.namedGlyphClass(
            "MNG:unmarked.A",
            [
                self.getDefault(alias, position)
                for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                for position in (init, medi, fina)
            ],
        )
        markedVariants = c.namedGlyphClass(
            "MNG:marked.A",
            [
                self.getDefault(alias, position, True)
                for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                for position in (init, medi, fina)
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
                for position in (init, medi):
                    unmarked = self.getDefault(alias, position)
                    self.sub(c.input(unmarked, _marked), cl["MNG:vowelMasculine"])
            for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]:
                unmarked = self.getDefault(alias, fina)
                self.sub(c.input(unmarked, _marked), cl["mvs"], cl["MNG:a.isol"])

        with c.Lookup(
            "III.ig.preprocessing.H", feature="rclt", flags={"UseMarkFilteringSet": femiClass}
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (init, medi):
                    unmarked = self.getDefault(alias, position)
                    marked = self.getDefault(alias, position, True)
                    c.rsub(c.input(unmarked), markedVariants, by=marked)

        with c.Lookup("III.ig.preprocessing.I", feature="rclt"):
            for alias in ["h", "g"]:
                for position in (init, medi):
                    marked = self.getDefault(alias, position, True)
                    self.sub(c.input(marked, _unmarked), masc)

        with c.Lookup("III.ig.preprocessing.J", feature="rclt"):
            markedVariants = c.namedGlyphClass(
                "MNG:marked.B",
                [
                    self.getDefault(alias, position, True)
                    for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                    if alias not in ["h", "g"]
                    for position in (init, medi, fina)
                ],
            )
            self.sub(c.input(markedVariants, _unmarked))

        with c.Lookup("III.ig.preprocessing.K", feature="rclt"):
            for alias in ["h", "g"]:
                for position in (init, medi):
                    unmarked = self.getDefault(alias, position)
                    marked = self.getDefault(alias, position, True)
                    self.sub(marked, by=[unmarked, masc])

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
            aLike = c.variants("MNG", ["a", "e"], isol)
            with c.Lookup("III.a_e.chachlag", feature="rclt", flags={"IgnoreMarks": True}):
                c.sub(c.input(cl["mvs"], cd["_.narrow"]), c.input(aLike, cd["MNG:chachlag"]))

            with c.Lookup(
                "III.a_e.chachlag.GB", feature="rclt", flags={"UseMarkFilteringSet": cl["fvs"]}
            ):
                c.sub(c.input(cl["mvs"], cd["_.reset"]), aLike, cl["fvs"])

    def iii2(self):
        """
        **Phase III.2: Phonetic - Syllabic**
        """

        self.iii2a()
        self.iii2b()
        self.iii2c()
        self.iii2d()
        self.iii2e()
        self.iii2f()
        self.iii2g()

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
                    c.sub(
                        cl["MNG:consonant.init"],
                        c.input(c.variants("MNG", ["o", "u", "oe", "ue"]), cd["MNG:marked"]),
                    )
                if "MNGx" in self.locales:
                    c.sub(
                        cl["MNGx:consonant.init"],
                        c.input(c.variants("MNGx", ["o", "ue"]), cd["MNGx:marked"]),
                    )
                    c.sub(
                        cl["MNGx:consonant.init"],
                        cl["MNGx:hX"],
                        c.input(cl["MNGx:ue"], cd["MNGx:marked"]),
                    )
                for locale in ["SIB", "MCH", "MCHx"]:
                    if locale in self.locales:
                        c.sub(
                            cl[f"{locale}:consonant.init"],
                            c.input(c.variants(locale, ["o", "u"]), cd[f"{locale}:marked"]),
                        )

        if "MNG" in self.locales:
            with c.Lookup(
                "III.o_u_oe_ue.marked.GB.A",
                feature="rclt",
                flags={"UseMarkFilteringSet": cl["fvs"]},
            ):
                variants = c.variants("MNG", ["o", "u", "oe", "ue"], (medi, fina))
                c.sub(c.input(variants, cd["MNG:reset"]), cl["fvs"])
                c.sub(cl["fvs"], c.input(variants, cd["MNG:reset"]))

            with c.Lookup(
                "III.o_u_oe_ue.marked.GB.B",
                feature="rclt",
                flags={"UseMarkFilteringSet": cl["fvs"]},
            ):
                c.sub(
                    c.variants("MNG", ["g", "h"], init),
                    c.glyphClass([cl["fvs2"], cl["fvs4"]]),
                    c.input(c.variants("MNG", ["oe", "ue"], fina), cd["MNG:marked"]),
                )

            markedVariants = c.namedGlyphClass(
                "MNG:marked.C",
                [
                    self.getDefault(alias, position, True)
                    for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]
                    for position in (init, medi, fina)
                ],
            )
            with c.Lookup(
                "III.o_u_oe_ue.initial_marked.GB.A", feature="rclt", flags={"IgnoreMarks": True}
            ):
                c.sub(
                    c.glyphClass([cl["MNG:consonant.init"], markedVariants]),
                    c.input(cl["MNG:consonant.medi"], cd["_.marked.MNG"]),
                )

            variants = c.variants("MNG", ["o", "u", "oe", "ue"], medi)
            with c.Lookup(
                "III.o_u_oe_ue.initial_marked.GB.B", feature="rclt", flags={"IgnoreMarks": True}
            ):
                c.sub(
                    c.glyphClass([cl["MNG:consonant.init"], markedVariants]),
                    c.input(variants, cd["MNG:marked"]),
                )

            with c.Lookup("III.o_u_oe_ue.initial_marked.GB.C", feature="rclt"):
                c.sub(c.input(markedVariants, cd["_.unmarked.MNG"]))

            with c.Lookup("III.d.marked", feature="rclt", flags={"IgnoreMarks": True}):
                c.sub(c.input(cl["MNG:d.init"], cd["MNG:marked"]), cl["MNG:vowel.fina"])

            with c.Lookup(
                "III.d.marked.GB", feature="rclt", flags={"UseMarkFilteringSet": cl["fvs"]}
            ):
                c.sub(c.input(cl["MNG:d.init"], cd["MNG:reset"]), cl["MNG:vowel.fina"], cl["fvs"])
                c.sub(c.input(cl["MNG:d.init"], cd["MNG:reset"]), cl["fvs"], cl["MNG:vowel.fina"])

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
                    c.sub(c.input(cl["SIB:z"], cd["SIB:marked"]), cl["SIB:i"])
                if "MCH" in self.locales:
                    c.sub(cl["MCH:z"], c.input(cl["MCH:i"], cd["MCH:marked"]))
                    c.sub(
                        c.input(cl["MCH:f"], cd["MCH:marked"]),
                        c.variants("MCH", ["i", "o", "u", "ue"]),
                    )
                if "MCHx" in self.locales:
                    c.sub(
                        c.variants("MCHx", ["cX", "z", "jhX"]),
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
                njwVariants = c.variants("MNG", ["n.fina", "j.isol", "j.fina", "w.fina"])
                hgVariants = c.variants("MNG", ["h", "g"], "fina")
                if "MNG" in self.locales:
                    c.sub(
                        c.input(njwVariants, cd["MNG:chachlag_onset"]),
                        cl["mvs.valid"],
                        c.glyphClass(["u1820.Aa.isol", "u1821.Aa.isol"]),
                    )
                    c.sub(
                        c.input(hgVariants, cd["MNG:chachlag_onset"]),
                        cl["mvs.valid"],
                        "u1820.Aa.isol",
                    )
                if "MNGx" in self.locales:
                    c.sub(
                        c.input(cl["MNGx:a.fina"], cd["MNG:chachlag_onset"]),
                        cl["mvs.valid"],
                        "u1820.Aa.isol",
                    )

        if "MNG" in self.locales:
            with c.Lookup(
                "III.g.chachlag_onset.MNG.GB", feature="rclt", flags={"IgnoreMarks": True}
            ):
                c.sub(
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
        cd = self.conditions

        if {"SIB", "MCH", "MCHx"}.intersection(self.locales):
            with c.Lookup(
                "III.e_u.feminine.SIB_MCH_MCHx", feature="rclt", flags={"IgnoreMarks": True}
            ):
                for locale in ["SIB", "MCH", "MCHx"]:
                    if locale in self.locales:
                        consonants = c.variants(locale, ["t", "d", "k", "g", "h"])
                        if locale == "MCHx":
                            consonants = c.variants(
                                "MCHx", ["tX", "t", "d", "dhX", "g", "k", "ghX", "h"]
                            )
                        euLetters = c.variants(locale, ["e", "u"])
                        c.sub(consonants, c.input("u1860.Oh.fina", cd[f"{locale}:feminine_marked"]))
                        c.sub(consonants, c.input(euLetters, cd[f"{locale}:feminine"]))

                        if locale == "MCHx":
                            c.sub(
                                c.variants("MCHx", ["ngX", "sbm"]),
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
                        c.sub(
                            c.input(cl[f"{locale}:n"], cd[f"{locale}:onset"]), cl[f"{locale}:vowel"]
                        )
                        c.sub(
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
                    c.sub(
                        c.input(c.variants("MNG", ["t", "d"], init)),
                        cl["MNG:vowel.fina"],
                        ignore=True,
                    )
                    tLike = c.variants("MNG", ["t", "d"])
                    c.sub(c.input(tLike, cd["MNG:onset"]), cl["MNG:vowel"])
                    c.sub(c.input(tLike, cd["MNG:devsger"]), cl["MNG:consonant"])
                for locale in ["SIB", "MCH", "MCHx"]:
                    if locale in self.locales:
                        tLike = c.variants(locale, ["t", "d"])
                        if locale == "MCHx":
                            tLike = c.variants("MCHx", ["tX", "dhX"])
                        aLike = c.variants(locale, ["a", "i", "o"])
                        eLike = c.variants(locale, ["e", "u", "ue"])
                        c.sub(c.input(tLike, cd[f"{locale}:masculine_onset"]), aLike)
                        c.sub(c.input(tLike, cd[f"{locale}:feminine"]), eLike)
                        if locale != "MCHx":
                            c.sub(
                                c.input(cl[f"{locale}:t"], cd[f"{locale}:devsger"]),
                                cl[f"{locale}:consonant"],
                            )
                            c.sub(
                                cl[f"{locale}:vowel"],
                                c.input(cl[f"{locale}:t.fina"], cd[f"{locale}:devsger"]),
                            )

    def iii2f(self):
        """
        (1) When (_k_,) _g_, _h_ precedes masculine vowel, apply `masculine_onset`. When (_k_,) _g_, _h_ precedes feminine or neuter vowel, apply `feminine`. Apply `masculine_devsger` or `feminine` or `devsger` for Hudum, Todo, Sibe, Manchu in devsger context.

        (2) For Hudum, when _g_, _h_ following _i_ precedes masculine indicator, apply `masculine_devsger`, else apply `feminine`. When initial _g_, _h_ precedes a consonant, apply `feminine`.

        (3) Delete all the masculine indicators and the feminine indicators after _g_ or _h_.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        masc, femi = "masculine", "feminine"
        mascClass, femiClass = c.glyphClass([masc]), c.glyphClass([femi])

        if {"MNG", "TOD", "SIB", "MCH"}.intersection(self.locales):
            with c.Lookup(
                "III.k_g_h.onset_and_devsger_and_gender.MNG_TOD_SIB_MCH",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                for locale in ["MNG", "TOD", "SIB", "MCH"]:
                    if locale in self.locales:
                        gLikeAliases = ["h", "g"] if locale in ["MNG", "TOD"] else ["k", "g", "h"]
                        gLike = c.variants(locale, gLikeAliases)

                        if locale == "MNG":
                            aLike = c.variants("MNG", ["a", "e"], isol)
                            c.sub(c.input(gLike), cl["mvs"], aLike, ignore=True)
                        c.sub(
                            c.input(gLike, cd[f"{locale}:masculine_onset"]),
                            cl[f"{locale}:vowelMasculine"],
                        )
                        c.sub(
                            c.input(gLike, cd[f"{locale}:feminine"]),
                            c.variants(locale, ["vowelFeminine", "vowelNeuter"]),
                        )
                if "MNG" in self.locales:
                    gLike = c.variants("MNG", ["h", "g"])
                    c.sub(cl["MNG:vowelMasculine"], c.input(gLike, cd["MNG:masculine_devsger"]))
                    c.sub(cl["MNG:vowelFeminine"], c.input(gLike, cd["MNG:feminine"]))
                if "TOD" in self.locales:
                    c.sub(cl["TOD:vowel"], c.input(cl["TOD:g"], cd["TOD:masculine_devsger"]))
                if "SIB" in self.locales:
                    c.sub(c.input(cl["SIB:k"], cd["SIB:devsger"]), cl["SIB:consonant"])
                    c.sub(cl["SIB:vowel"], c.input(cl["SIB:k.fina"], cd["SIB:devsger"]))
                if "MCH" in self.locales:
                    c.sub(
                        cl["MCH:t"], cl["MCH:e"], c.input(cl["MCH:k"], cd["MCH:masculine_devsger"])
                    )
                    gLike = c.variants("MCH", ["k", "g", "h"])
                    c.sub(gLike, cl["MCH:u"], c.input(cl["MCH:k"], cd["MCH:feminine"]))
                    ghLike = c.variants("MCH", ["kh", "gh", "hh"])
                    c.sub(ghLike, cl["MCH:a"], c.input(cl["MCH:k"], cd["MCH:feminine"]))
                    c.sub(c.variants("MCH", ["e", "ue"]), c.input(cl["MCH:k"], cd["MCH:feminine"]))
                    c.sub(
                        c.variants("MCH", ["a", "i", "o", "u"]),
                        c.input(cl["MCH:k"], cd["MCH:masculine_devsger"]),
                    )

        if "MNG" in self.locales:
            with c.Lookup(
                "III.g_h.onset_and_devsger_and_gender.A.MNG",
                feature="rclt",
                flags={"UseMarkFilteringSet": mascClass},
            ):
                gLike = c.variants("MCH", ["h", "g"])
                aLike = c.variants("MNG", ["a", "e"], isol)
                c.sub(c.input(gLike), cl["MNG:vowel"], ignore=True)
                c.sub(c.input(gLike), masc, cl["MNG:vowel"], ignore=True)
                c.sub(c.input(gLike), cl["mvs"], aLike, ignore=True)
                c.sub(c.input(gLike), cl["mvs"], masc, aLike, ignore=True)
                c.sub(cl["MNG:i"], c.input(gLike, cd["MNG:masculine_devsger"]), masc)
                c.sub(cl["MNG:i"], c.input(cl["MNG:g"], cd["MNG:feminine"]))

            with c.Lookup(
                "III.g_h.onset_and_devsger_and_gender.B.MNG",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                c.sub(
                    c.input(c.variants("MNG", ["h", "g"], init), cd["MNG:feminine"]),
                    cl["MCH:consonant"],
                )

            for index in [0, 1]:
                step = ["A", "B"][index]
                genderGlyph = [masc, femi][index]
                genderClass = [mascClass, femiClass][index]

                with c.Lookup(
                    f"III.ig.post_processing.{step}.MNG",
                    feature="rclt",
                    flags={"UseMarkFilteringSet": genderClass},
                ):
                    for alias in ["h", "g"]:
                        charName = getCharNameByAlias("MNG", alias)
                        for position in (init, medi, fina):
                            variants = data.variants[charName].get(position, {})
                            for i in variants.values():
                                variant = str(GlyphDescriptor.fromData(charName, position, i))
                                c.sub(variant, genderGlyph, by=variant)

    def iii2g(self):
        """
        (1) When _t_ precedes _ee_ or consonant, apply `devsger`.

        (2) When _sh_ precedes _i_ and not in Twelve Syllabaries, apply `dotless`.

        (3) When _g_ follows _s_ or _d_, apply `dotless`.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        if "MNG" in self.locales:
            with c.Lookup("III.t_sh_g.MNG.GB", feature="rclt", flags={"IgnoreMarks": True}):
                c.sub(
                    c.input(cl["MNG:t"], cd["MNG:devsger"]), c.variants("MNG", ["ee", "consonant"])
                )
                c.sub(c.input(cl["MNG:sh.init"], cd["MNG:dotless"]), cl["MNG:i.medi"])
                c.sub(
                    c.input(cl["MNG:sh.medi"], cd["MNG:dotless"]),
                    c.variants("MNG", "i", (medi, fina)),
                )
                c.sub(
                    c.variants("MNG", ["s", "d"]),
                    c.input(cl["MNG:g.medi"], cd["MNG:dotless"]),
                    cl["MNG:vowelMasculine"],
                )
                c.sub(
                    c.variants("MNG", ["s", "d"]),
                    c.input(cl["MNG:g.fina"], cd["MNG:dotless"]),
                    cl["mvs"],
                    "u1820.Aa.isol",
                )

    def iii3(self):
        """
        (1) Apply `particle` for letters in particles following MVS in Hudum, Todo, Sibe and Manchu.

        (2) Apply `particle` for letters in particles not following MVS in Hudum.

        (3) According to GB, apply `_.wide` for MVS preceding Hudum string in Hudum.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        for locale in ["MNG", "SIB", "MCH"]:
            if locale in self.locales:
                with c.Lookup(
                    f"III.particle.{locale}",
                    feature="rclt",
                    flags={"UseMarkFilteringSet": cl["fvs"]},
                ):
                    for aliasString, indices in data.particles[locale].items():
                        aliasList = aliasString.split()
                        hasMvs = aliasList[0] == "mvs"
                        if hasMvs:
                            aliasList = aliasList[1:]
                            indices = [index - 1 for index in indices]
                        classList = []

                        position = lambda i, l: (
                            isol if l == 1 else (init if i == 0 else fina if i == l - 1 else medi)
                        )
                        classList = [
                            cl[f"{locale}:{alias}.{position(index, len(aliasList))}"]
                            for index, alias in enumerate(aliasList)
                        ]

                        subArgs: list = [c.input(cl["mvs"], cd["_.wide"])] if hasMvs else []
                        ignoreSubArgs: list = [c.input(cl["mvs"])] if hasMvs else []
                        minIndex = 0 if hasMvs else min(indices)
                        for i, glyphClass in enumerate(classList):
                            if i in indices:
                                subArgs.append(c.input(glyphClass, cd[f"{locale}:particle"]))
                                ignoreSubArgs.append(c.input(glyphClass))
                            elif minIndex <= i <= max(indices):
                                subArgs.append(c.input(glyphClass))
                                ignoreSubArgs.append(c.input(glyphClass))
                            else:
                                subArgs.append(glyphClass)
                                ignoreSubArgs.append(glyphClass)
                        c.sub(*subArgs)
                        c.sub(*ignoreSubArgs, cl["fvs"], ignore=True)

        if "TOD" in self.locales:
            with c.Lookup("TOD:particle") as _particle:
                c.sub(cl["TOD:n.init"], by="u1828.N.init.mvs")

            with c.Lookup("III.particle.TOD", feature="rclt", flags={"IgnoreMarks": True}):
                c.sub(
                    c.input(cl["mvs"], cd["_.wide"]),
                    c.input(cl["TOD:n.init"], _particle),
                    cl["TOD:i.fina"],
                )

        if "MNG" in self.locales:
            with c.Lookup("III.mvs.postprocessing.GB", feature="rclt"):
                c.sub(
                    c.input(cl["mvs.invalid"], cd["_.wide"]),
                    c.glyphClass(
                        [cl["MNG:vowel"], cl["MNG:consonant"], "nirugu", "nirugu.ignored"]
                    ),
                )

    def iii4(self):
        """
        (1) Apply `devsger` for _i_ and _u_ in Hudum, Todo, Sibe and Manchu.

        (2) According to GB, reset _i_ in some contexts.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        if {"MNG", "TOD", "SIB", "MCH", "MCHx"}.intersection(self.locales):
            with c.Lookup(
                "III.i_u.devsger.MNG_TOD_SIB_MCH_MCHx", feature="rclt", flags={"IgnoreMarks": True}
            ):
                if "MNG" in self.locales:
                    vowelVariants = c.namedGlyphClass(
                        "MNG:vowel.not_ending_with_I",
                        [
                            str(GlyphDescriptor.fromData(charName, position, variant))
                            for charName in [
                                getCharNameByAlias("MNG", alias)
                                for alias in data.locales["MNG"].categories["vowel"]
                            ]
                            for position in (init, medi)
                            for variant in data.variants[charName].get(position, {}).values()
                            if not variant.written[-1] == "I"
                        ],
                    )
                    c.sub(vowelVariants, c.input(cl["MNG:i"], cd["MNG:vowel_devsger"]))
                if "TOD" in self.locales:
                    c.sub(cl["TOD:vowel"], c.input(cl["TOD:i"], cd["TOD:vowel_devsger"]))
                    c.sub(cl["TOD:u"], c.input(cl["TOD:u"], cd["TOD:vowel_devsger"]))
                if "SIB" in self.locales:
                    c.sub(cl["SIB:vowel"], c.input(cl["SIB:i"], cd["SIB:vowel_devsger"]))
                    c.sub(cl["SIB:vowel"], c.input(cl["SIB:u"], cd["SIB:vowel_devsger"]))
                if "MCH" in self.locales:
                    c.sub(cl["MCH:vowel"], c.input(cl["MCH:i"], cd["MCH:vowel_devsger"]))
                if "MCHx" in self.locales:
                    c.sub(cl["MCHx:vowel"], c.input(cl["MCHx:u"], cd["MCHx:vowel_devsger"]))

        if "MNG" in self.locales:
            with c.Lookup(
                "III.i.devsger.MNG.GB", feature="rclt", flags={"UseMarkFilteringSet": cl["fvs"]}
            ):
                c.sub(
                    c.variants("MNG", ["oe", "ue"], medi),
                    c.glyphClass([cl["fvs1"], cl["fvs2"]]),
                    c.input(c.variants("MNG", "i", (medi, fina)), cd["MNG:reset"]),
                )
                c.sub(
                    c.variants("MNG", ["oe", "ue"], medi),
                    cl["fvs3"],
                    c.input(cl["MNG:i"], cd["MNG:vowel_devsger"]),
                )
                c.sub(
                    cl["MNG:ue.init"],
                    cl["fvs2"],
                    c.input(c.variants("MNG", "i", (medi, fina)), cd["MNG:reset"]),
                )
                c.sub(cl["MNG:ue.medi"], cl["fvs1"], c.input(cl["MNG:i"], cd["MNG:vowel_devsger"]))

    def iii5(self):
        """
        (1) Apply `post_bowed` for vowel following bowed consonant for Hudum, Hudum Ali Gali, Todo, Todo Ali Gali, Sibe, Manchu and Manchu Ali Gali.

        (2) According to GB, adjust the vowel (may precede FVS) following bowed consonant for Hudum.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        if "MNG" in self.locales:
            bowedB = c.namedGlyphClass("MNG:bowedB", c.variants("MNG", ["b", "p", "f"]).glyphs)
            bowedK = c.namedGlyphClass("MNG:bowedK", c.variants("MNG", ["k", "k2"]).glyphs)
            bowedG = c.namedGlyphClass(
                "MNG:bowedG", c.variants("MNG", ["h", "g"], (init, medi), ["G", "Gx"]).glyphs
            )
            with c.Lookup("III.vowel.post_bowed.MNG", feature="rclt", flags={"IgnoreMarks": True}):
                bowed = c.glyphClass([bowedB, bowedK, bowedG])
                c.sub(bowed, c.input(c.glyphClass(["u1825.Ue.fina", "u1826.Ue.fina"])), ignore=True)
                c.sub(
                    bowed,
                    c.input(c.variants("MNG", ["o", "u", "oe", "ue"], fina), cd["MNG:post_bowed"]),
                )
                c.sub(
                    c.glyphClass([bowedB, bowedK]),
                    c.input(c.variants("MNG", ["a", "e"], fina), cd["MNG:post_bowed"]),
                )
                c.sub(bowedG, c.input(c.variants("MNG", "e", fina), cd["MNG:post_bowed"]))

            with c.Lookup(
                "III.vowel.post_bowed.MNG.GB",
                feature="rclt",
                flags={"UseMarkFilteringSet": cl["fvs"]},
            ):
                hgVariants = c.variants("MNG", ["h", "g"])
                c.sub(
                    hgVariants,
                    c.glyphClass([cl["fvs2"], cl["fvs4"]]),
                    c.input(cl["MNG:e.fina"], cd["MNG:post_bowed"]),
                )
                c.sub(
                    hgVariants,
                    c.glyphClass([cl["fvs1"], cl["fvs3"]]),
                    c.input(cl["MNG:e.fina"], cd["MNG:reset"]),
                )
                c.sub(
                    c.variants("MNG", ["b", "p", "f", "k", "k2"], init),
                    cl["fvs"],
                    c.input(c.variants("MNG", ["oe", "ue"], fina), cd["MNG:marked"]),
                )
                c.sub(
                    hgVariants,
                    c.glyphClass([cl["fvs1"], cl["fvs3"]]),
                    c.input(c.variants("MNG", ["o", "u", "oe", "ue"], fina), cd["MNG:reset"]),
                )
                c.sub(
                    c.variants("MNG", ["g", "h"], (init, medi)),
                    c.glyphClass([cl["fvs2"], cl["fvs4"]]),
                    c.input(c.variants("MNG", ["o", "u"], fina), cd["MNG:reset"]),
                )
                c.sub(
                    c.variants("MNG", ["g", "h"], medi),
                    c.glyphClass([cl["fvs2"], cl["fvs4"]]),
                    c.input(c.variants("MNG", ["oe", "ue"], fina), cd["MNG:post_bowed"]),
                )
                c.sub(
                    c.variants("MNG", ["g", "h"], init),
                    c.glyphClass([cl["fvs2"], cl["fvs4"]]),
                    c.input(c.variants("MNG", ["oe", "ue"], fina), cd["MNG:marked"]),
                )

        if "MNGx" in self.locales:
            bowedB = c.namedGlyphClass("MNGx:bowedB", c.variants("MNGx", ["pX", "phX", "b"]).glyphs)
            bowedK = c.namedGlyphClass("MNGx:bowedK", c.variants("MNGx", ["kX", "k2", "k"]).glyphs)
            with c.Lookup("III.vowel.post_bowed.MNGx", feature="rclt", flags={"IgnoreMarks": True}):
                bowed = c.glyphClass([bowedB, bowedK])
                vowels = ["a", "o", "ue"]
                c.sub(bowed, c.input(c.variants("MNGx", vowels, fina), cd["MNGx:post_bowed"]))
                c.sub(cl["MNGx:waX"], c.input(cl["MNGx:a"]), by="u1820.Aa.isol.post_wa")

        if "TOD" in self.locales:
            bowedB = c.namedGlyphClass("TOD:bowedB", c.variants("TOD", ["b", "p"]).glyphs)
            bowedK = c.namedGlyphClass("TOD:bowedK", c.variants("TOD", ["kh", "gh"]).glyphs)
            bowedG = c.namedGlyphClass(
                "TOD:bowedG",
                c.variants("TOD", "h", (init, medi), "K").glyphs
                + c.variants("TOD", "g", (init, medi), "G").glyphs,
            )
            with c.Lookup("III.vowel.post_bowed.TOD", feature="rclt", flags={"IgnoreMarks": True}):
                bowed = c.glyphClass([bowedB, bowedK, bowedG])
                vowels = ["a", "i", "u", "ue"]
                c.sub(bowed, c.input(c.variants("TOD", vowels, fina), cd["TOD:post_bowed"]))

                c.sub(bowed, c.input(cl["TOD:a_lvs.fina"]), by="u1820_u1843.AaLv.fina")

        if "TODx" in self.locales:
            bowedB = c.namedGlyphClass("TODx:bowedB", c.variants("TODx", ["pX", "p", "b"]).glyphs)
            bowedK = c.namedGlyphClass(
                "TODx:bowedK", c.variants("TODx", ["kX", "khX", "gX"]).glyphs
            )
            with c.Lookup("III.vowel.post_bowed.TODx", feature="rclt", flags={"IgnoreMarks": True}):
                bowed = c.glyphClass([bowedB, bowedK])
                vowels = ["a", "i", "ue"]
                c.sub(bowed, c.input(c.variants("TODx", vowels, fina), cd["TODx:post_bowed"]))

                c.sub(bowed, c.input(cl["TODx:a_lvs.fina"]), by="u1820_u1843.AaLv.fina")
                c.sub(bowed, c.input(cl["TODx:i_lvs.fina"]), by="u1845_u1843.IpLv.fina")
                c.sub(bowed, c.input(cl["TODx:ue_lvs.fina"]), by="u1849_u1843.OLv.fina")

        for locale in ["SIB", "MCH"]:
            if locale in self.locales:
                bowedB = c.namedGlyphClass(
                    f"{locale}:bowedB", c.variants(locale, ["b", "p"]).glyphs
                )
                bowedK = c.namedGlyphClass(
                    f"{locale}:bowedK", c.variants(locale, ["kh", "gh", "hh"]).glyphs
                )
                bowedG = c.namedGlyphClass(
                    f"{locale}:bowedG",
                    c.variants(locale, "k", (init, medi), ["G", "Gx"]).glyphs
                    + c.variants(locale, "g", (init, medi), "Gh").glyphs
                    + c.variants(locale, "h", (init, medi), "Gc").glyphs,
                )
                with c.Lookup(
                    f"III.vowel.post_bowed.{locale}", feature="rclt", flags={"IgnoreMarks": True}
                ):
                    c.sub(
                        c.glyphClass([bowedB, bowedG]),
                        c.input(c.variants(locale, ["e", "u"]), cd[f"{locale}:post_bowed"]),
                    )
                    c.sub(
                        c.glyphClass([bowedB, bowedK]),
                        c.input(c.variants(locale, ["a", "o"]), cd[f"{locale}:post_bowed"]),
                    )

        if "MCHx" in self.locales:
            bowedB = c.namedGlyphClass(
                "MCHx:bowedB", c.variants("MCHx", ["pX", "p", "b", "bhX"]).glyphs
            )
            bowedK = c.namedGlyphClass("MCHx:bowedK", c.variants("MCHx", ["gh", "kh"]).glyphs)
            bowedG = c.namedGlyphClass(
                "MCHx:bowedG",
                c.variants("MCHx", "k", (init, medi), "G").glyphs
                + c.variants("MCHx", "g", (init, medi), "Gh").glyphs
                + c.variants("MCHx", "h", (init, medi), "Gc").glyphs,
            )
            with c.Lookup("III.vowel.post_bowed.MCHx", feature="rclt", flags={"IgnoreMarks": True}):
                c.sub(
                    c.glyphClass([bowedB, bowedG, cl["MCHx:ghX"]]),
                    c.input(c.variants("MCHx", ["e", "u"]), cd["MCHx:post_bowed"]),
                )
                c.sub(
                    c.glyphClass([cl["MCHx:ngX"], cl["MCHx:sbm"]]),
                    c.input(cl["MCHx:e"], cd["MCHx:post_bowed"]),
                )
                c.sub(
                    c.glyphClass([bowedB, bowedK]),
                    c.input(c.variants("MCHx", ["a", "o"]), cd["MCHx:post_bowed"]),
                )

    def iii6(self):
        """
        (1) Apply `manual` for letters preceding FVS.

        (2) Apply `manual` for letters preceding FVS that precedes LVS for Todo and Todo Ali Gali.

        (3) Apply `manual` for punctuation.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        for locale in self.locales:
            with c.Lookup(f"_.manual.{locale}") as _lvs:
                for alias in getAliasesByLocale(locale):
                    charName = getCharNameByAlias(locale, alias)
                    letter = locale + ":" + alias
                    for position, variants in data.variants[charName].items():
                        glyphClass = cl[letter + "." + position]
                        for fvs, variant in variants.items():
                            if fvs != 0:
                                variant = str(GlyphDescriptor.fromData(charName, position, variant))
                                c.sub(c.input(glyphClass), f"fvs{fvs}.ignored", by=variant)

            with c.Lookup(f"III.fvs.{locale}", feature="rclt"):
                for alias in getAliasesByLocale(locale):
                    charName = getCharNameByAlias(locale, alias)
                    letter = locale + ":" + alias
                    for position, variants in data.variants[charName].items():
                        glyphClass = cl[letter + "." + position]
                        for fvs in variants:
                            if fvs != 0:
                                c.sub(
                                    c.input(glyphClass, _lvs),
                                    c.input(f"fvs{fvs}.ignored", cd["_.valid"]),
                                )

        if "TOD" in self.locales:
            with c.Lookup("_.manual.lvs.TOD") as _lvs:
                c.sub(c.input(cl["TOD:a_lvs.isol"]), "fvs1.ignored", by="u1820_u1843.ALv.isol")
                c.sub(c.input(cl["TOD:a_lvs.isol"]), "fvs3.ignored", by="u1820_u1843.AALv.isol")
                c.sub(c.input(cl["TOD:a_lvs.init"]), "fvs2.ignored", by="u1820_u1843.AALv.init")
                c.sub(c.input(cl["TOD:a_lvs.fina"]), "fvs1.ignored", by="u1820_u1843.AaLv.fina")
                c.sub(c.input(cl["TOD:a_lvs.fina"]), "fvs2.ignored", by="u1820_u1843.AaLv.fina")
            with c.Lookup("III.fvs.lvs.TOD"):
                c.sub(c.input(cl["TOD:a_lvs.isol"], _lvs), c.input("fvs1.ignored", cd["_.valid"]))
                c.sub(c.input(cl["TOD:a_lvs.isol"], _lvs), c.input("fvs3.ignored", cd["_.valid"]))
                c.sub(c.input(cl["TOD:a_lvs.init"], _lvs), c.input("fvs2.ignored", cd["_.valid"]))
                c.sub(c.input(cl["TOD:a_lvs.fina"], _lvs), c.input("fvs1.ignored", cd["_.valid"]))
                c.sub(c.input(cl["TOD:a_lvs.fina"], _lvs), c.input("fvs2.ignored", cd["_.valid"]))

        if "TODx" in self.locales:
            with c.Lookup("_.manual.lvs.TODx") as _lvs:
                c.sub(c.input(cl["TODx:i_lvs.fina"]), "fvs1.ignored", by="u1845_u1843.IpLv.fina")
                c.sub(c.input(cl["TODx:i_lvs.fina"]), "fvs2.ignored", by="u1845_u1843.I3Lv.fina")
                c.sub(c.input(cl["TODx:ue_lvs.fina"]), "fvs1.ignored", by="u1849_u1843.OLv.fina")
                c.sub(c.input(cl["TODx:ue_lvs.fina"]), "fvs2.ignored", by="u1849_u1843.ULv.fina")
            with c.Lookup("III.fvs.lvs.TODx"):
                c.sub(c.input(cl["TODx:i_lvs.fina"], _lvs), c.input("fvs1.ignored", cd["_.valid"]))
                c.sub(c.input(cl["TODx:i_lvs.fina"], _lvs), c.input("fvs2.ignored", cd["_.valid"]))
                c.sub(c.input(cl["TODx:ue_lvs.fina"], _lvs), c.input("fvs1.ignored", cd["_.valid"]))
                c.sub(c.input(cl["TODx:ue_lvs.fina"], _lvs), c.input("fvs2.ignored", cd["_.valid"]))

        with c.Lookup("_.manual.punctuation") as _lvs:
            c.sub(c.input("u1880"), "fvs1.ignored", by="u1880.fvs1")
            c.sub(c.input("u1881"), "fvs1.ignored", by="u1881.fvs1")

        with c.Lookup("III.fvs.punctuation", feature="rclt"):
            c.sub(c.input("u1880", _lvs), c.input("fvs1.ignored", cd["_.valid"]))
            c.sub(c.input("u1881", _lvs), c.input("fvs1.ignored", cd["_.valid"]))

    def iib1(self):
        """
        Ligatures.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        for locale in self.locales:
            for ligature in data.ligatures:
                ...

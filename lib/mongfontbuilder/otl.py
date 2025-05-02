import operator
import re
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from functools import reduce
from itertools import product

from fontTools import unicodedata
from fontTools.feaLib import ast
from tptq.feacomposer import AnyGlyph, ContextualInput, FeaComposer, _NormalizedAnyGlyph
from ufoLib2.objects import Font

from . import (
    GlyphDescriptor,
    composeGlyph,
    data,
    getPosition,
    splitWrittens,
    uNameFromCodePoint,
    writtenCombinations,
)
from .data.misc import JoiningPosition, fina, init, isol, joiningPositions, medi
from .data.types import FVS, LocaleID
from .utils import getAliasesByLocale, getCharNameByAlias, namespaceFromLocale

masculineMarker, feminineMarker = "_masculine", "_feminine"


@dataclass
class MongFeaComposer(FeaComposer):
    font: Font | None
    locales: list[LocaleID]
    classes: dict[str, ast.GlyphClassDefinition]
    conditions: dict[str, ast.LookupBlock]
    gdef: dict[str, list]

    def __init__(
        self,
        font: Font | None,
        locales: list[LocaleID] = [*data.locales],
    ) -> None:
        for locale in locales:
            assert locale.removesuffix("x") in locales

        self.font = font
        self.locales = locales

        super().__init__(
            languageSystems={
                "mong": {"dflt"} | {namespaceFromLocale(i).ljust(4) for i in self.locales}
            }
        )
        self.classes = {}
        self.conditions = {}
        self.gdef = {}

        self.initControls()
        self.initVariants()

        self.ia1()
        self.iia1()
        self.iii0()
        self.iii1()
        self.iii2()
        self.iii3()
        self.iii4()
        self.iii5()
        self.iii6()
        self.iib1()
        self.iib2()
        self.iib3()
        self.ib1()
        self.ib2()

        self.writeGdef()

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

    def namedGlyphClass(
        self, name: str, glyphs: Iterable[AnyGlyph] | ast.GlyphClass
    ) -> ast.GlyphClassDefinition:
        if isinstance(glyphs, ast.GlyphClass):
            glyphs = glyphs.glyphs
        definition = ast.GlyphClassDefinition(name, self.glyphClass(glyphs))
        self.current.append(definition)
        return definition

    def newGlyph(self, name: str):
        if self.font is not None:
            self.font.lib.get("public.glyphOrder", []).append(name)
            return self.font.newGlyph(name)

    def writeGdef(self):
        gdefBlock = ast.TableBlock("GDEF")
        gdefBlock.statements.append(
            ast.GlyphClassDefStatement(
                baseGlyphs=self.glyphClass(self.gdef.get("base", [])),
                ligatureGlyphs=self.glyphClass(self.gdef.get("ligature", [])),
                markGlyphs=self.glyphClass(self.gdef.get("mark", [])),
                componentGlyphs=self.glyphClass(self.gdef.get("component", [])),
            )
        )
        self.current.append(gdefBlock)

    def initControls(self):
        """
        Initialize glyph classes and condition lookups for control characters.

        For FVSes, `@fvs.ignored` indicates the state that needs to be ignored before FVS lookup, `@fvs.valid` indicates the state that is successfully matched after FVS lookup, and `@fvs.invalid` indicates the state that is not matched after FVS lookup.

        For MVS, `@mvs.valid` indicates the state that is successfully matched after chachlag or particle lookups, and `@mvs.invalid` indicates the state that is not matched after chachlag and particle lookups.

        For nirugu, `nirugu.ignored` indicates the nirugu as a `mark` that needs to be ignored, and `nirugu` indicate the valid nirugu as a `base`.
        """

        fvses = [f"fvs{i}" for i in range(1, 5)]
        for fvs in fvses:
            variants = [fvs]
            for suffix in [".valid", ".ignored"]:
                variant = fvs + suffix
                self.newGlyph(variant)
                variants.append(variant)
            self.classes[fvs] = self.namedGlyphClass(fvs, variants)

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

        self.gdef.setdefault("base", []).extend([self.classes["fvs.invalid"], self.classes["mvs"]])
        self.gdef.setdefault("mark", []).extend(
            [self.classes["fvs.valid"], self.classes["fvs.ignored"]]
        )

        with self.Lookup("_.ignored") as _ignored:
            for original in ["nirugu", "zwj", "zwnj"]:
                variant = original + ".ignored"
                self.newGlyph(variant)
                self.sub(original, by=variant)

            self.gdef.setdefault("base", []).extend(["nirugu", "zwj", "zwnj", "zwj.ignored"])
            self.gdef.setdefault("mark", []).extend(["nirugu.ignored", "zwnj.ignored"])

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
                lvsPositionalClasses = list[ast.GlyphClassDefinition]()
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

                    lvsVariants = [
                        GlyphDescriptor.fromData(charName, position, i)
                        for i in variants.values()
                        if locale in i.locales and i.locales[locale].lvs
                    ]
                    if lvsVariants:
                        lvsVariants = [
                            str(
                                GlyphDescriptor(
                                    v.codePoints + [0x1843], v.units + ["Lv"], v.position
                                )
                            )
                            for v in lvsVariants
                        ]
                        lvsPositionalClass = self.namedGlyphClass(
                            letter + "_lvs." + position, lvsVariants
                        )
                        self.classes[letter + "_lvs." + position] = lvsPositionalClass
                        lvsPositionalClasses.append(lvsPositionalClass)

                letterClass = self.namedGlyphClass(letter, positionalClasses)
                self.classes[letter] = letterClass
                if genderNeutralCategory != category:
                    categoryToClasses.setdefault(locale + ":" + genderNeutralCategory, []).append(
                        letterClass
                    )
                categoryToClasses.setdefault(locale + ":" + category, []).append(letterClass)

                if lvsPositionalClasses:
                    letterClass = self.namedGlyphClass(letter + "_lvs", lvsPositionalClasses)
                    self.classes[letter + "_lvs"] = letterClass
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
    ) -> ast.GlyphClass:
        """
        >>> composer = MongFeaComposer(font=None)
        >>> composer.variants("MNG", ["a", "o", "u"], fina).asFea()
        '[@MNG:a.fina @MNG:o.fina @MNG:u.fina]'
        """
        aliases = [aliases] if isinstance(aliases, str) else aliases
        positions = [positions] if isinstance(positions, str) else positions
        return self.glyphClass(
            self.classes[f"{locale}:{alias}" + (f".{position}" if position else "")]
            for alias in aliases
            for position in positions or [None]
        )

    def variant(
        self, locale: LocaleID, alias: str, position: JoiningPosition, fvs: FVS = 0
    ) -> GlyphDescriptor:
        """
        >>> composer = MongFeaComposer(font=None)
        >>> str(composer.variant("MCH", "zr", fina))
        'u1877.Jc.medi._fina'
        >>> str(composer.variant("MCHx", "zr", fina))
        'u1877.Jc.fina'
        """
        charName = getCharNameByAlias(locale, alias)
        variant = data.variants[charName][position][fvs]
        return GlyphDescriptor.fromData(charName, position, variant, locale=locale)

    def writtens(
        self,
        locale: LocaleID,
        writtens: str | Iterable[str] | Callable[[list[str]], bool],
        positions: JoiningPosition | Iterable[JoiningPosition] | None = None,
        aliases: list[str] = [],
    ) -> ast.GlyphClass:
        """
        >>> composer = MongFeaComposer(font=None)
        >>> composer.writtens("MNG", "A", medi).asFea()
        '[u1820.A.medi u1821.A.medi u1828.A.medi]'
        """
        positions = (
            joiningPositions
            if positions is None
            else ([positions] if isinstance(positions, str) else positions)
        )
        aliases = aliases or getAliasesByLocale(locale)
        if isinstance(writtens, Callable):
            filter, writtens = writtens, [
                "".join(self.variant(locale, alias, position, fvs).units)
                for alias in aliases
                for position in positions
                for fvs in data.variants[getCharNameByAlias(locale, alias)][position].keys()
            ]
        else:
            writtens = [writtens] if isinstance(writtens, str) else list(writtens)
            filter = lambda _: True

        glyphs = []
        for alias in aliases:
            charName = getCharNameByAlias(locale, alias)
            for position in positions:
                for written in writtens:
                    if "Lv" not in written:
                        variants = [
                            w
                            for fvs in data.variants[charName][position].keys()
                            if (w := self.variant(locale, alias, position, fvs)).units
                            == splitWrittens(written)
                            and filter(w.units)
                        ]
                    else:
                        variants = []
                        key = f"{locale}:{alias}_lvs.{position}"
                        if key in self.classes:
                            variants = [
                                GlyphDescriptor.parse(g.glyph)
                                for g in self.classes[key].glyphs.glyphs
                                if written in g.glyph
                                and filter(GlyphDescriptor.parse(g.glyph).units)
                            ]
                    glyphs.extend(str(v) for v in variants if str(v) not in glyphs)
        return self.glyphClass(glyphs)

    def ia1(self) -> None:
        """
        **Phase Ia.1: Basic character-to-glyph mapping**

        Since Unicode Version 16.0, NNBSP has been taken over by MVS, which participate in chachlag and particle shaping.
        """

        with self.Lookup("Ia.nnbsp.preprocessing", feature="ccmp"):
            self.sub("nnbsp", by="mvs")

    def iia1(self) -> None:
        """
        **Phase IIa.1: Initiation of cursive positions**
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
            c.sub(c.input(c.glyphClass(["zwnj", "zwj", "nirugu", cl["fvs"]]), cd["_.ignored"]))

        with c.Lookup("III.mvs.preserving.A", feature="rclt"):
            c.sub("mvs", by=["mvs.wide", "mvs.wide"])

        with c.Lookup("III.mvs.preserving.B", feature="rclt"):
            c.sub("mvs.wide", "mvs.wide", by="mvs")

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

    def getDefault(
        self,
        alias: str,
        position: JoiningPosition,
        *,
        marked: bool = False,
    ) -> str:
        name = str(
            GlyphDescriptor.fromData(
                getCharNameByAlias("MNG", alias),
                position,
                suffixes=["marked"] if marked else [],
            )
        )
        if marked and name not in (self.font or []):
            self.newGlyph(name)
        return name

    def iii0b(self):
        """
        GB requires that the masculinity and femininity of a letter be passed forward and backward indefinitely throughout the word.

        A to C implement masculinity indefinitely passing forward, D to F implement femininity indefinitely passing forward, G to K implement masculinity indefinitely passing backward.
        """

        c = self
        cl = self.classes
        cd = self.conditions
        ct = data.locales["MNG"].categories

        # add masculine

        self.newGlyph(masculineMarker)
        self.gdef.setdefault("mark", []).append(masculineMarker)

        with c.Lookup("III.ig.preprocessing.A", feature="rclt"):
            for alias in ct["vowelMasculine"]:
                for position in (init, medi):
                    default = self.getDefault(alias, position)
                    self.sub(default, by=[default, masculineMarker])

        with c.Lookup(
            "III.ig.preprocessing.B",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.glyphClass([masculineMarker])},
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (medi, fina):
                    default = self.getDefault(alias, position)
                    self.sub(masculineMarker, c.input(default), by=[default, masculineMarker])

        with c.Lookup("III.ig.preprocessing.C", feature="rclt"):
            for alias in ct["vowelMasculine"] + ct["vowelNeuter"] + ct["consonant"]:
                if alias not in ["h", "g"]:
                    for position in (init, medi, fina):
                        default = self.getDefault(alias, position)
                        self.sub(default, masculineMarker, by=default)

        # add feminine

        self.newGlyph(feminineMarker)
        self.gdef.setdefault("mark", []).append(feminineMarker)

        with c.Lookup("III.ig.preprocessing.D", feature="rclt"):
            for alias in ct["vowelFeminine"]:
                for position in (init, medi):
                    default = self.getDefault(alias, position)
                    self.sub(default, by=[default, feminineMarker])

        with c.Lookup(
            "III.ig.preprocessing.E",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.glyphClass([feminineMarker])},
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (medi, fina):
                    default = self.getDefault(alias, position)
                    self.sub(feminineMarker, c.input(default), by=[default, feminineMarker])

        with c.Lookup("III.ig.preprocessing.F", feature="rclt"):
            for alias in ct["vowelFeminine"] + ct["vowelNeuter"] + ct["consonant"]:
                if alias not in ["h", "g"]:
                    for position in (init, medi, fina):
                        default = self.getDefault(alias, position)
                        self.sub(default, feminineMarker, by=default)

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
                self.getDefault(alias, position, marked=True)
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
            "III.ig.preprocessing.H",
            feature="rclt",
            flags={"UseMarkFilteringSet": c.glyphClass([feminineMarker])},
        ):
            for alias in ct["vowelNeuter"] + ct["consonant"]:
                for position in (init, medi):
                    unmarked = self.getDefault(alias, position)
                    marked = self.getDefault(alias, position, marked=True)
                    c.rsub(c.input(unmarked), markedVariants, by=marked)

        with c.Lookup("III.ig.preprocessing.I", feature="rclt"):
            for alias in ["h", "g"]:
                for position in (init, medi):
                    marked = self.getDefault(alias, position, marked=True)
                    self.sub(c.input(marked, _unmarked), masculineMarker)

        with c.Lookup("III.ig.preprocessing.J", feature="rclt"):
            markedVariants = c.namedGlyphClass(
                "MNG:marked.B",
                [
                    self.getDefault(alias, position, marked=True)
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
                    marked = self.getDefault(alias, position, marked=True)
                    self.sub(marked, by=[unmarked, masculineMarker])

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
                    self.getDefault(alias, position, marked=True)
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

        if {"MNG", "TOD", "SIB", "MCH"}.intersection(self.locales):
            gLike = lambda locale: c.variants(
                locale, ["h", "g"] if locale in ["MNG", "TOD"] else ["k", "g", "h"]
            )

            with c.Lookup(
                "III.k_g_h.onset_and_devsger_and_gender.MNG_TOD_SIB_MCH",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                if "MNG" in self.locales:
                    c.sub(
                        c.input(gLike("MNG")),
                        cl["mvs"],
                        c.variants("MNG", ["a", "e"], isol),
                        ignore=True,
                    )
                for locale in ["MNG", "TOD", "SIB", "MCH"]:
                    if locale in self.locales:
                        c.sub(
                            c.input(gLike(locale), cd[f"{locale}:masculine_onset"]),
                            cl[f"{locale}:vowelMasculine"],
                        )

                for locale in ["MNG", "TOD", "SIB", "MCH"]:
                    if locale in self.locales:
                        c.sub(
                            c.input(gLike(locale), cd[f"{locale}:feminine"]),
                            c.glyphClass(
                                [cl[f"{locale}:vowelFeminine"], cl[f"{locale}:vowelNeuter"]]
                            ),
                        )

                if "MNG" in self.locales:
                    c.sub(
                        cl["MNG:vowelMasculine"], c.input(gLike("MNG"), cd["MNG:masculine_devsger"])
                    )
                    c.sub(cl["MNG:vowelFeminine"], c.input(gLike("MNG"), cd["MNG:feminine"]))
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
                flags={"UseMarkFilteringSet": c.glyphClass([masculineMarker])},
            ):
                gLike = c.variants("MNG", ["h", "g"])
                aLike = c.variants("MNG", ["a", "e"], isol)
                c.sub(c.input(gLike), cl["MNG:vowel"], ignore=True)
                c.sub(c.input(gLike), masculineMarker, cl["MNG:vowel"], ignore=True)
                c.sub(c.input(gLike), cl["mvs"], aLike, ignore=True)
                c.sub(c.input(gLike), masculineMarker, cl["mvs"], aLike, ignore=True)
                c.sub(cl["MNG:i"], c.input(gLike, cd["MNG:masculine_devsger"]), masculineMarker)
                c.sub(cl["MNG:i"], c.input(cl["MNG:g"], cd["MNG:feminine"]))

            with c.Lookup(
                "III.g_h.onset_and_devsger_and_gender.B.MNG",
                feature="rclt",
                flags={"IgnoreMarks": True},
            ):
                c.sub(
                    c.input(c.variants("MNG", ["h", "g"], init), cd["MNG:feminine"]),
                    cl["MNG:consonant"],
                )

            for index in [0, 1]:
                step = ["A", "B"][index]
                genderMarker = [masculineMarker, feminineMarker][index]

                with c.Lookup(
                    f"III.ig.post_processing.{step}.MNG",
                    feature="rclt",
                    flags={"UseMarkFilteringSet": c.glyphClass([genderMarker])},
                ):
                    for alias in ["h", "g"]:
                        charName = getCharNameByAlias("MNG", alias)
                        for position in (init, medi, fina):
                            variants = data.variants[charName].get(position, {})
                            for i in variants.values():
                                variant = str(GlyphDescriptor.fromData(charName, position, i))
                                c.sub(variant, genderMarker, by=variant)

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
        **Phase III.3: Phonetic - Particle**

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

                        classList = [
                            cl[f"{locale}:{alias}.{getPosition(index, len(aliasList))}"]
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
                        c.sub(*ignoreSubArgs, cl["fvs"], ignore=True)
                        c.sub(*subArgs)

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
        **Phase III.4: Graphemic - Devsger**

        (1) Apply `devsger` for _i_ and _u_ in Hudum, Todo, Sibe and Manchu.

        (2) According to GB, reset _i_ in some contexts.
        """

        c = self
        cl = self.classes
        cd = self.conditions
        ct = data.locales["MNG"].categories

        if {"MNG", "TOD", "SIB", "MCH", "MCHx"}.intersection(self.locales):
            with c.Lookup(
                "III.i_u.devsger.MNG_TOD_SIB_MCH_MCHx", feature="rclt", flags={"IgnoreMarks": True}
            ):
                if "MNG" in self.locales:
                    vowelVariants = c.namedGlyphClass(
                        "MNG:vowel.not_ending_with_I",
                        c.writtens("MNG", lambda x: x[-1] != "I", (init, medi), ct["vowel"]),
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
                c.sub(cl["MNG:ue.init"], cl["fvs1"], c.input(cl["MNG:i"], cd["MNG:vowel_devsger"]))

    def iii5(self):
        """
        **Phase III.5: Graphemic - Post-bowed**

        (1) Apply `post_bowed` for vowel following bowed consonant for Hudum, Hudum Ali Gali, Todo, Todo Ali Gali, Sibe, Manchu and Manchu Ali Gali.

        (2) According to GB, adjust the vowel (may precede FVS) following bowed consonant for Hudum.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        if "MNG" in self.locales:
            bowedB = c.namedGlyphClass("MNG:bowedB", c.variants("MNG", ["b", "p", "f"]))
            bowedK = c.namedGlyphClass("MNG:bowedK", c.variants("MNG", ["k", "k2"]))
            bowedG = c.namedGlyphClass("MNG:bowedG", c.writtens("MNG", ["G", "Gx"]))

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

            with c.Lookup("III.fvs.post_bowed.preprocessing.GB", feature="rclt"):
                c.sub(
                    c.glyphClass([bowedB, bowedK, bowedG]),
                    c.input(cl["fvs.ignored"], cd["_.reset"]),
                )

            with c.Lookup(
                "III.vowel.post_bowed.MNG.GB", feature="rclt", flags={"IgnoreMarks": True}
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

            with c.Lookup("III.fvs.post_bowed.postprocessing.GB", feature="rclt"):
                c.sub(
                    c.glyphClass([bowedB, bowedK, bowedG]),
                    c.input(cl["fvs.invalid"], cd["_.ignored"]),
                )

        if "MNGx" in self.locales:
            bowedB = c.namedGlyphClass("MNGx:bowedB", c.variants("MNGx", ["pX", "phX", "b"]))
            bowedK = c.namedGlyphClass("MNGx:bowedK", c.variants("MNGx", ["kX", "k2", "k"]))
            with c.Lookup("III.vowel.post_bowed.MNGx", feature="rclt", flags={"IgnoreMarks": True}):
                bowed = c.glyphClass([bowedB, bowedK])
                vowels = ["a", "o", "ue"]
                c.sub(bowed, c.input(c.variants("MNGx", vowels, fina), cd["MNGx:post_bowed"]))
                c.sub(cl["MNGx:waX"], c.input(cl["MNGx:a"]), by="u1820.Aa.isol.post_wa")

        if "TOD" in self.locales:
            bowedB = c.namedGlyphClass("TOD:bowedB", c.variants("TOD", ["b", "p"]))
            bowedK = c.namedGlyphClass("TOD:bowedK", c.variants("TOD", ["kh", "gh"]))
            bowedG = c.namedGlyphClass("TOD:bowedG", c.writtens("TOD", ["K", "G"]))
            with c.Lookup("III.vowel.post_bowed.TOD", feature="rclt", flags={"IgnoreMarks": True}):
                bowed = c.glyphClass([bowedB, bowedK, bowedG])
                vowels = ["a", "i", "u", "ue"]
                c.sub(bowed, c.input(c.variants("TOD", vowels, fina), cd["TOD:post_bowed"]))

                c.sub(bowed, c.input(cl["TOD:a_lvs.fina"]), by="u1820_u1843.AaLv.fina")

        if "TODx" in self.locales:
            bowedB = c.namedGlyphClass("TODx:bowedB", c.variants("TODx", ["pX", "p", "b"]))
            bowedK = c.namedGlyphClass("TODx:bowedK", c.variants("TODx", ["kX", "khX", "gX"]))
            with c.Lookup("III.vowel.post_bowed.TODx", feature="rclt", flags={"IgnoreMarks": True}):
                bowed = c.glyphClass([bowedB, bowedK])
                vowels = ["a", "i", "ue"]
                c.sub(bowed, c.input(c.variants("TODx", vowels, fina), cd["TODx:post_bowed"]))

                c.sub(bowed, c.input(cl["TODx:a_lvs.fina"]), by="u1820_u1843.AaLv.fina")
                c.sub(bowed, c.input(cl["TODx:i_lvs.fina"]), by="u1845_u1843.IpLv.fina")
                c.sub(bowed, c.input(cl["TODx:ue_lvs.fina"]), by="u1849_u1843.OLv.fina")

        for locale in ["SIB", "MCH"]:
            if locale in self.locales:
                bowedB = c.namedGlyphClass(f"{locale}:bowedB", c.variants(locale, ["b", "p"]))
                bowedK = c.namedGlyphClass(
                    f"{locale}:bowedK", c.variants(locale, ["kh", "gh", "hh"])
                )
                bowedG = c.namedGlyphClass(
                    f"{locale}:bowedG", c.writtens(locale, ["G", "Gx", "Gh", "Gc"])
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
            bowedB = c.namedGlyphClass("MCHx:bowedB", c.variants("MCHx", ["pX", "p", "b", "bhX"]))
            bowedK = c.namedGlyphClass("MCHx:bowedK", c.variants("MCHx", ["gh", "kh"]))
            bowedG = c.namedGlyphClass("MCHx:bowedG", c.writtens("MCHx", ["G", "Gh", "Gc"]))
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
        **Phase III.6: Uncaptured - FVS-selected**

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

        if "MNGx" in self.locales:
            with c.Lookup("_.manual.punctuation") as _lvs:
                c.sub(c.input("u1880"), "fvs1.ignored", by="u1880.fvs1")
                c.sub(c.input("u1881"), "fvs1.ignored", by="u1881.fvs1")

            with c.Lookup("III.fvs.punctuation", feature="rclt"):
                c.sub(c.input("u1880", _lvs), c.input("fvs1.ignored", cd["_.valid"]))
                c.sub(c.input("u1881", _lvs), c.input("fvs1.ignored", cd["_.valid"]))

            self.gdef.setdefault("mark", []).extend(["u1885", "u1886", "u18A9"])

    def iterLigatureSubstitutions(
        self,
        writtens: str,
        position: JoiningPosition,
        locale: LocaleID,
    ) -> Iterator[tuple[tuple[GlyphDescriptor, ...], GlyphDescriptor]]:
        for combination in writtenCombinations(writtens, position):
            writtenLists = [
                [
                    GlyphDescriptor.parse(glyph.glyph)
                    for glyph in self.writtens(locale, *units.split(".")).glyphs  # type: ignore
                ]
                for units in combination
            ]
            for variants in product(*writtenLists):
                yield variants, reduce(operator.add, variants)

    def iib1(self):
        """
        **Phase IIb.1: Variation involving bowed written units**

        Ligatures.
        """

        c = self
        cl = self.classes

        with c.Lookup(
            f"IIb.ligature",
            feature="rclt",
            flags={  # Prevent ligation
                "UseMarkFilteringSet": c.glyphClass(["nirugu.ignored", cl["fvs.ignored"]])
            },
        ):
            inputToLigatureAndRequired = dict[
                tuple[GlyphDescriptor, ...], tuple[GlyphDescriptor, bool]
            ]()
            for locale in self.locales:
                namespace = namespaceFromLocale(locale)
                vowelAliases = data.locales[locale].categories["vowel"]
                for category, ligatureToPositions in data.ligatures.items():
                    for writtens, positions in ligatureToPositions.items():
                        for position in positions:
                            for input, ligature in c.iterLigatureSubstitutions(
                                writtens, position, locale
                            ):
                                if len(input) != 2:
                                    continue
                                if required := category == "required":
                                    # Check the second glyph, ignoring LVS:
                                    codePoint = input[1].codePoints[0]
                                    alias = data.aliases[unicodedata.name(chr(codePoint))]
                                    if isinstance(alias, dict):
                                        alias = alias[namespace]
                                    if alias not in vowelAliases:
                                        continue
                                # Deduplicate inputs:
                                inputToLigatureAndRequired[input] = ligature, required

            for input, (ligature, required) in inputToLigatureAndRequired.items():
                input = [str(i) for i in input]
                ligatureName = str(ligature)
                if self.font is None:
                    self.sub(*input, by=ligatureName)
                else:
                    if required and ligatureName not in self.font:
                        componentName = str(GlyphDescriptor([], ligature.units, ligature.position))
                        composeGlyph(self.font, ligatureName, [self.font[componentName]])
                    if ligatureName in self.font:
                        self.sub(*input, by=ligatureName)

            if "MNGx" in self.locales:
                c.sub("u18A6.Wp.medi", "u1820.A.fina", by="u18A6_u1820.WpA.fina")
                c.sub("u188A.NG.init", "u1820.Aa.fina", by="u188A_u1820.NGAa.isol")
                c.sub("u188A.NG.medi", "u1820.Aa.fina", by="u188A_u1820.NGAa.fina")
            if "TODx" in self.locales:
                # TODO
                ...
            if "MCH" in self.locales:
                c.sub("u186F.Zs.init", "u1873.I.fina", by="u186F_u1873.Zs.isol")
                c.sub("u186F.Zs.medi", "u1873.I.fina", by="u186F_u1873.Zs.fina")

    def iib2(self):
        """
        **Phase IIb.2: Cleanup of format controls**

        Controls postprocessing.
        """

        c = self
        cl = self.classes
        cd = self.conditions

        with c.Lookup("IIb.controls.postprocessing", feature="rclt"):
            c.sub(
                c.input(c.glyphClass(["nirugu.ignored", cl["fvs.ignored"]]), cd["_.reset"]),
            )

    def iib3(self):
        """
        **Phase IIb.3: Optional treatments**

        Optional treatments.
        """
        pass

    def ib1(self):
        """
        **Phase Ib.1: Vertical forms of punctuation marks**

        Vertical forms of punctuation.
        """
        pass

    def ib2(self):
        """
        **Phase Ib.2: Optional treatments**

        Optional treatments.
        """
        pass

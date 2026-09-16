import re
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, replace
from typing import cast

from fontTools import unicodedata
from fontTools.feaLib import ast
from tptq.feacomposer import FeaComposer

from .. import GlyphDescriptor, data, splitWrittens, uNameFromCodePoint, writtenCombinations
from ..data import codePointToCmapVariant
from ..data.logic import choosesLvs, choosesVariant
from ..data.types import (
    FVS,
    CharacterName,
    JoiningPosition,
    LocaleID,
    VariantData,
    WrittenUnitID,
    joiningPositions,
)
from ..spec import FontSpec, GlyphSpec
from ..utils import getAliasesByLocale, getCharNameByAlias, getVariants, namespaceFromLocale


@dataclass
class MongFeaComposer(FeaComposer):
    cmap: dict[int, str]
    glyphs: list[str]
    locales: list[LocaleID]
    spec: FontSpec

    # Internal states:
    classes: dict[str, ast.GlyphClassDefinition]
    conditions: dict[str, ast.LookupBlock]

    def __init__(
        self,
        *,
        cmap: dict[int, str],
        glyphs: list[str],
        locales: list[LocaleID],
    ) -> None:
        self.cmap = cmap
        self.glyphs = glyphs
        for locale in locales:
            assert locale.removesuffix("x") in locales
        self.locales = locales
        self.spec = FontSpec(cmap={}, newGlyphs={}, openTypeCategories={})

        # Every writing system keeps its own namespace (glyph classes, lookups and
        # conditions are all prefixed with the locale), so several writing systems can
        # be composed into one font. `self.locale` is the primary writing system; it is
        # only used where the output can carry a single answer for a character that is
        # shared between writing systems (see `iia`).
        self.writingSystems: list[LocaleID] = [
            cast(LocaleID, locale.removesuffix("x"))
            for locale in dict.fromkeys(locale.removesuffix("x") for locale in self.locales)
        ]
        self.locale: LocaleID = self.writingSystems[0]

        self.classes = {}
        self.conditions = {}

        super().__init__(
            languageSystems={
                # The default script is declared beside the Mongolian one so that a lookup
                # can be written for a layout that does not resolve its text to `mong` —
                # a layout reads the features of the script its text is written with, and
                # one that resolves to another script reads `DFLT`.
                "DFLT": {"dflt"},
                "mong": {"dflt"} | {namespaceFromLocale(i).ljust(4) for i in self.locales},
            }
        )

    def compose(self) -> FontSpec:
        from . import ia, ib, iia, iib, iii

        self.initWrittenUnits()
        self.constructPredefinedGlyphs()
        self.initControls()
        self.initVariants()
        for name in ["u1885", "u1886", "u18A9"]:
            processedName = self.glyphNameProcessor(name)
            if processedName in self.glyphs:
                self.spec.openTypeCategories[processedName] = "mark"

        ia.compose(self)
        iia.compose(self)
        iii.compose(self)
        iib.compose(self)
        ib.compose(self)

        return self.spec

    def initWrittenUnits(self) -> None:
        """Create the written units that are drawn as a control character.

        The nirugu written unit is the nirugu itself: the source font carries the
        control glyph, and `_Ni.medi` is built from it for the writing systems that
        write with it. It is built before everything else, because the written forms
        that join with the nirugu are built as components of it.
        """

        if not self.isWrittenUnitUsed("Ni"):
            return

        niruguName = self.glyphNameProcessor("nirugu")
        name = self.glyphNameProcessor("_Ni.medi")
        self.spec.newGlyphs[name] = GlyphSpec([niruguName] if niruguName in self.glyphs else [])

    def isWrittenUnitUsed(self, unit: WrittenUnitID) -> bool:
        """Whether any targeted writing system writes with *unit*.

        A written unit is only needed where a written form of one of the targeted
        writing systems is written with it; the nirugu, for example, is written by Sibe
        and by Manchu.
        """

        for charName, positionsToFVSToVariant in data.variants.items():
            for position, variant, locale in self.usedVariants(charName, positionsToFVSToVariant):
                written = GlyphDescriptor.fromData(charName, position, variant, locale=locale)
                if unit in written.units:
                    return True
        return False

    def usedVariants(
        self,
        charName: CharacterName,
        positionsToFVSToVariant: dict[JoiningPosition, dict[FVS, VariantData]],
    ) -> Iterator[tuple[JoiningPosition, VariantData, LocaleID]]:
        """Every variant of *charName* that a targeted writing system resolves for itself.

        A variant may be shared by several writing systems, and each of them resolves its
        own written form, so one answer is given per writing system, in the order the
        writing systems are targeted.
        """

        for position, fvsToVariant in positionsToFVSToVariant.items():
            for variant in fvsToVariant.values():
                for locale in self.locales:
                    if locale in variant.locales:
                        yield position, variant, locale

    def constructPredefinedGlyphs(self) -> None:
        sources = list[GlyphDescriptor]()
        for name in self.glyphs:
            try:
                source = GlyphDescriptor.parse(name)
            except (AssertionError, ValueError):
                continue
            sources.append(source)

        codePointToVariantGlyph = dict[int, str]()
        for charName, positionsToFVSToVariant in data.variants.items():
            variantNames = [
                self.constructPredefinedGlyph(sources, charName, position, variant, locale)
                for position, variant, locale in self.usedVariants(
                    charName, positionsToFVSToVariant
                )
            ]
            if not variantNames:
                continue

            codePoint = ord(unicodedata.lookup(charName))
            # A character whose default variant is written differently in every writing
            # system has no cross-locale written form, hence no cmap entry.
            if resolved := codePointToCmapVariant.get(codePoint):
                codePointToVariantGlyph[codePoint] = str(GlyphDescriptor([codePoint], *resolved))

        for codePoint, variantGlyph in codePointToVariantGlyph.items():
            processedName = self.glyphNameProcessor(uNameFromCodePoint(codePoint))
            self.spec.cmap[codePoint] = processedName
            self.spec.newGlyphs[processedName] = GlyphSpec([self.glyphNameProcessor(variantGlyph)])

    def constructPredefinedGlyph(
        self,
        sources: list[GlyphDescriptor],
        charName: CharacterName,
        position: JoiningPosition,
        variant: VariantData,
        locale: LocaleID,
    ) -> str:
        """Create the glyph of *variant* as *locale* writes it, and name it.

        Each writing system resolves its own written form of a shared variant, and so does
        every extension of a writing system — `MNGx` beside `MNG` — so the locale is not
        reduced to its namespace here. The written form itself is a glyph of its own — the
        one the source font draws and the written form lookups reference — so the variant
        is built as a component of it unless the source font already carries it. A variant
        is written with the padding of the position it borrows its shape from, which may
        not be its own.
        """

        target = GlyphDescriptor.fromData(charName, position, variant, locale=locale)
        targetName = str(target)
        if self.glyphNameProcessor(targetName) in self.glyphs:
            return targetName

        writtenTarget = replace(target, codePoints=[], suffixes=[])
        memberNames = _findMemberNames(sources, writtenTarget)
        glyphSpec = GlyphSpec([self.glyphNameProcessor(i) for i in memberNames])
        if pseudoPosition := target.pseudoPosition():
            glyphSpec.initPadding = pseudoPosition in ["isol", "init"]
            glyphSpec.finaPadding = pseudoPosition in ["isol", "fina"]
        self.spec.newGlyphs[self.glyphNameProcessor(targetName)] = glyphSpec
        return targetName

    def constructLvsGlyphs(self, variants: list[GlyphDescriptor]) -> None:
        """Create the glyph of each long vowel sign variant.

        A long vowel sign variant is drawn as the written form it follows plus `Lv`,
        which the source font carries as one written form — `_AALv.isol` draws
        `u1820_u1843.AALv.isol` — so the variant is built as a component of it rather
        than stored in the source font. The written form names itself: a descriptor
        without code points is already written with a leading `_`.
        """

        for variant in variants:
            name = self.glyphNameProcessor(str(variant))
            if name in self.spec.newGlyphs:
                continue
            written = str(GlyphDescriptor([], variant.units, variant.position))
            member = self.glyphNameProcessor(written)
            self.spec.newGlyphs[name] = GlyphSpec([member] if member in self.glyphs else [])

    def initControls(self) -> None:
        """
        Initialize glyph classes and condition lookups for control characters.

        For FVSes, `@fvs.ignored` indicates the state that needs to be ignored before FVS lookup, `@fvs.valid` indicates the state that is successfully matched after FVS lookup, and `@fvs.invalid` indicates the state that is not matched after FVS lookup.

        For MVS, `@mvs.valid` indicates the state that is successfully matched after chachlag or particle lookups, and `@mvs.invalid` indicates the state that is not matched after chachlag and particle lookups.

        For nirugu, `nirugu.ignored` indicates the nirugu as a `mark` that needs to be ignored, and `nirugu` indicate the valid nirugu as a `base`.
        """

        from .iii import (
            MARKER_FEMININE,
            MARKER_INITIAL,
            MARKER_MASCULINE,
            MARKER_MASCULINE_FALSE,
            MARKER_MASCULINE_TRUE,
        )

        fvses = [f"fvs{i}" for i in range(1, 5)]
        for fvs in fvses:
            variants = [fvs]
            for suffix in [".valid", ".ignored"]:
                variant = fvs + suffix
                variants.append(variant)
                self.spec.newGlyphs[self.glyphNameProcessor(variant)] = GlyphSpec([])
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

        for glyphClass in [self.classes["fvs.invalid"], self.classes["mvs"]]:
            for glyphName in glyphClass.glyphSet():
                self.spec.openTypeCategories[glyphName.glyph] = "base"
        for glyphClass in [self.classes["fvs.valid"], self.classes["fvs.ignored"]]:
            for glyphName in glyphClass.glyphSet():
                self.spec.openTypeCategories[glyphName.glyph] = "mark"

        # `nbspace` (a clone of `space` carrying NO-BREAK SPACE U+00A0), the wide MVS
        # (which draws as a space) and the zero-width ignored `mvs.ignored` are set up
        # here, alongside the other control glyphs, so they are created early and appear
        # early in glyph order. `iib2` later splits a wide MVS into `nbspace` +
        # `mvs.ignored`.
        spaceName = self.glyphNameProcessor("space")
        nbspaceName = self.glyphNameProcessor("nbspace")
        wideName = self.glyphNameProcessor("mvs.wide")
        ignoredName = self.glyphNameProcessor("mvs.ignored")
        self.spec.newGlyphs[nbspaceName] = GlyphSpec([spaceName])
        self.spec.newGlyphs[wideName] = GlyphSpec([spaceName])
        self.spec.newGlyphs[ignoredName] = GlyphSpec([])
        self.spec.cmap[0x00A0] = nbspaceName
        self.spec.openTypeCategories[ignoredName] = "mark"

        with self.Lookup("_.ignored") as _ignored:
            for original in ["nirugu", "zwj", "zwnj"]:
                variant = original + ".ignored"
                self.sub(original, by=variant)
                self.spec.newGlyphs[self.glyphNameProcessor(variant)] = GlyphSpec([])

            for name in ["nirugu"]:
                self.spec.openTypeCategories[self.glyphNameProcessor(name)] = "base"
            for name in ["nirugu.ignored", "zwj", "zwj.ignored", "zwnj", "zwnj.ignored"]:
                self.spec.openTypeCategories[self.glyphNameProcessor(name)] = "mark"

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

        if "MNG" in self.locales:
            for name in MARKER_MASCULINE, MARKER_FEMININE:
                processedName = self.glyphNameProcessor(name)
                self.spec.newGlyphs[processedName] = GlyphSpec([])
                self.spec.openTypeCategories[processedName] = "mark"
            for name in MARKER_MASCULINE_FALSE, MARKER_MASCULINE_TRUE:
                processedName = self.glyphNameProcessor(name)
                self.spec.newGlyphs[processedName] = GlyphSpec([])
                self.spec.openTypeCategories[processedName] = "base"
            processedName = self.glyphNameProcessor(MARKER_INITIAL)
            self.spec.newGlyphs[processedName] = GlyphSpec([])
            self.spec.openTypeCategories[processedName] = "mark"

    def initVariants(self) -> None:
        """
        Initialize glyph classes for variants.

        Initialize condition lookups for variants.

        Conditions generated from `variant.locales` -- locale + "-" + condition, e.g. `MNG-chachlag`.

        In addition, GB shaping requirements result in the need to reset the letter to its default variant. Resetting condition -- locale + "-reset", e.g. `MNG-reset`.
        """

        for locale in self.locales:
            categoryToClasses = dict[str, list[ast.GlyphClassDefinition]]()
            for alias in getAliasesByLocale(locale):
                self.initAliasVariants(locale, alias, categoryToClasses)

            for name, positionalClasses in categoryToClasses.items():
                self.classes[name] = self.namedGlyphClass(name, positionalClasses)

        for locale in self.locales:
            for condition in data.locales[locale].conditions:
                with self.Lookup(f"{locale}:{condition}") as lookup:
                    self.constructCondition(locale, condition)
                self.conditions[lookup.name] = lookup

        if "MNG" in self.locales:
            with self.Lookup("MNG:reset") as lookup:
                self.constructReset()
            self.conditions[lookup.name] = lookup

    def constructReset(self) -> None:
        """Reset every letter of Hudum to its default variant.

        A letter may carry the written form of another writing system when the writing
        systems share their letters — Manchu writes Hudum _a_ differently — so a letter
        that is written as a Hudum letter is reset to the Hudum written form.
        """

        for position in joiningPositions:
            for alias in getAliasesByLocale("MNG"):
                positionalClass = self.classes[f"MNG-{alias}.{position}"]
                charName = getCharNameByAlias("MNG", alias)
                default = str(GlyphDescriptor.fromData(charName, position))
                self.sub(positionalClass, by=default)

    def initAliasVariants(
        self,
        locale: LocaleID,
        alias: str,
        categoryToClasses: dict[str, list[ast.GlyphClassDefinition]],
    ) -> None:
        """Initialize the glyph classes of one letter of *locale*.

        `letterClass` -- locale + "-" + alias, e.g. `@MNG-a`.

        `categoryClass` -- locale + "-" + category (+ "." + position), e.g. `@MNG-vowel` or `@MNG-vowel.init`.

        A category class gathers the letters of a category, such as the vowels or the consonants of a writing system. A writing system that writes a category differently from the writing systems it shares its letters with answers both with its own category and with the gender-neutral one the category is derived from.
        """

        letter = locale + "-" + alias
        charName = getCharNameByAlias(locale, alias)
        category = next(k for k, v in data.locales[locale].categories.items() if alias in v)
        genderNeutralCategory = re.sub("[A-Z][a-z]+", "", category)
        categories = [category]
        if genderNeutralCategory != category:
            categories.insert(0, genderNeutralCategory)

        positionalClasses = list[ast.GlyphClassDefinition]()
        lvsPositionalClasses = list[ast.GlyphClassDefinition]()
        for position, variants in data.variants[charName].items():
            positionalClass, lvsPositionalClass = self.initPositionalClasses(
                locale, charName, letter, position, variants.values()
            )
            positionalClasses.append(positionalClass)
            categoryClasses(
                categoryToClasses, locale, genderNeutralCategory + "." + position, positionalClass
            )
            if lvsPositionalClass:
                lvsPositionalClasses.append(lvsPositionalClass)

        letterClass = self.namedGlyphClass(letter, positionalClasses)
        self.classes[letter] = letterClass
        for name in categories:
            categoryClasses(categoryToClasses, locale, name, letterClass)

        if not lvsPositionalClasses:
            return

        lvsLetterClass = self.namedGlyphClass(letter + "_lvs", lvsPositionalClasses)
        self.classes[letter + "_lvs"] = lvsLetterClass
        for name in categories:
            categoryClasses(categoryToClasses, locale, name, lvsLetterClass)

    def initPositionalClasses(
        self,
        locale: LocaleID,
        charName: CharacterName,
        letter: str,
        position: JoiningPosition,
        variants: Iterable[VariantData],
    ) -> tuple[ast.GlyphClassDefinition, ast.GlyphClassDefinition | None]:
        """Initialize the glyph classes of one joining position of a letter.

        `positionalClass` -- locale + "-" + alias + "." + position, e.g. `@MNG-a.isol`.

        `lvsPositionalClass` -- the same of the long vowel sign forms, e.g. `@MNG-a_lvs.isol`, or `None` when the letter has no long vowel sign form in the position.
        """

        descriptors = self.variantDescriptors(locale, charName, position, variants)
        positionalClass = self.namedGlyphClass(
            letter + "." + position, [str(i) for i in descriptors]
        )
        self.classes[letter + "." + position] = positionalClass

        lvsVariants = self.lvsVariantDescriptors(locale, charName, position, variants)
        if not lvsVariants:
            return positionalClass, None
        self.constructLvsGlyphs(lvsVariants)
        lvsPositionalClass = self.namedGlyphClass(
            letter + "_lvs." + position, [str(v) for v in lvsVariants]
        )
        self.classes[letter + "_lvs." + position] = lvsPositionalClass
        return positionalClass, lvsPositionalClass

    def constructCondition(self, locale: LocaleID, condition: str) -> None:
        """Offer every letter of *locale* the variant that answers *condition*.

        A condition is a property of the letters around a letter — the harmonic gender of
        its word, say — and every variant of a letter names the conditions it answers, so
        the lookup of a condition is the variants of that condition of every letter.
        """

        for alias in getAliasesByLocale(locale):
            self.constructAliasCondition(locale, alias, condition)

    def constructAliasCondition(self, locale: LocaleID, alias: str, condition: str) -> None:
        """Offer one letter of *locale* every variant it has that answers *condition*."""

        for _, charName, position, _, variant in getVariants(locale, [alias]):
            if not choosesVariant(locale, variant, condition):
                continue
            target = GlyphDescriptor.fromData(
                charName, position, variant, locale=namespaceFromLocale(locale)
            )
            self.sub(self.classes[f"{locale}-{alias}.{position}"], by=str(target))

    def variantDescriptors(
        self,
        locale: LocaleID,
        charName: CharacterName,
        position: JoiningPosition,
        variants: Iterable[VariantData],
    ) -> list[GlyphDescriptor]:
        """The written form of every variant that *locale* answers.

        A character whose variants differ per writing system resolves its written form
        per locale, so a variant that *locale* does not answer is left out. The written
        form is that of the writing system, not of one of its extensions.
        """

        return [
            GlyphDescriptor.fromData(charName, position, i, locale=locale)
            for i in variants
            if locale in i.locales
        ]

    def lvsVariantDescriptors(
        self,
        locale: LocaleID,
        charName: CharacterName,
        position: JoiningPosition,
        variants: Iterable[VariantData],
    ) -> list[GlyphDescriptor]:
        """The long vowel sign form of every written form that has one.

        A long vowel sign is drawn after the written form it follows, so the long vowel
        sign form is that written form with an `Lv` unit appended.
        """

        return [
            GlyphDescriptor([*v.codePoints, 0x1843], [*v.units, "Lv"], v.position)
            for v in self.variantDescriptors(
                locale, charName, position, [i for i in variants if choosesLvs(locale, i)]
            )
        ]

    def variants(
        self,
        locale: LocaleID,
        aliases: str | Iterable[str],
        positions: JoiningPosition | Iterable[JoiningPosition] | None = None,
    ) -> ast.GlyphClass:
        """
        >>> composer = MongFeaComposer(cmap={}, glyphs=[], locales=["MNG"])
        >>> composer.initVariants()
        >>> composer.variants("MNG", ["a", "o", "u"], "fina").asFea()
        '[@MNG-a.fina @MNG-o.fina @MNG-u.fina]'
        """
        aliases = [aliases] if isinstance(aliases, str) else aliases
        positions = [positions] if isinstance(positions, str) else positions
        return self.glyphClass(
            self.classes[f"{locale}-{alias}" + (f".{position}" if position else "")]
            for alias in aliases
            for position in positions or [None]
        )

    def writtens(
        self,
        locale: LocaleID,
        writtens: str | Iterable[str] | Callable[[list[str]], bool],
        positions: JoiningPosition | Iterable[JoiningPosition] | None = None,
        aliases: list[str] | None = None,
    ) -> ast.GlyphClass:
        """
        >>> composer = MongFeaComposer(cmap={}, glyphs=[], locales=["MNG"])
        >>> composer.writtens("MNG", "A", "medi").asFea()
        '[u1820.A.medi u1821.A.medi u1828.A.medi]'
        """
        positions = (
            joiningPositions
            if positions is None
            else ([positions] if isinstance(positions, str) else positions)
        )
        aliases = aliases or getAliasesByLocale(locale)
        if isinstance(writtens, Callable):
            filter, writtens = (
                writtens,
                [
                    "".join(variantGlyphDescriptor(locale, alias, position, fvs).units)
                    for alias in aliases
                    for position in positions
                    for fvs in data.variants[getCharNameByAlias(locale, alias)][position]
                ],
            )
        else:
            writtens = [writtens] if isinstance(writtens, str) else list(writtens)

            def filter(units: list[str], /) -> bool:
                return True

        glyphs = []
        for alias in aliases:
            for position in positions:
                for written in writtens:
                    variants = self.writtenVariants(locale, alias, position, written, filter)
                    glyphs.extend(str(v) for v in variants if str(v) not in glyphs)
        return self.glyphClass(glyphs)

    def writtenVariants(
        self,
        locale: LocaleID,
        alias: str,
        position: JoiningPosition,
        written: str,
        filter: Callable[[list[str]], bool],
    ) -> list[GlyphDescriptor]:
        """The variants of *alias* in *position* whose written form is *written*.

        A written form without `Lv` is carried by the variants themselves, matched by
        units; a written form with `Lv` is a long vowel sign form, built into the class of
        the long vowel sign variants and matched by glyph name.
        """

        if "Lv" in written:
            key = f"{locale}-{alias}_lvs.{position}"
            if key not in self.classes:
                return []
            return [
                GlyphDescriptor.parse(g.glyph)
                for g in self.classes[key].glyphs.glyphs
                if written in g.glyph and filter(GlyphDescriptor.parse(g.glyph).units)
            ]

        charName = getCharNameByAlias(locale, alias)
        return [
            w
            for fvs in data.variants[charName][position]
            if (w := variantGlyphDescriptor(locale, alias, position, fvs)).units
            == splitWrittens(written)
            and filter(w.units)
            and locale in data.variants[charName][position][fvs].locales
        ]

    def defaultVariant(self, charName: CharacterName, position: JoiningPosition) -> str:
        """The glyph that `position` maps a character to by default.

        A character shared between writing systems is written differently in each of
        them, but the font can only carry one answer for it. A real variant wins over a
        fabricated one — a variant borrowed from another joining position, marked by a
        `_position` suffix; among fabricated variants the first writing system in
        `self.locales` wins.
        """

        candidates = [
            GlyphDescriptor.fromData(charName, position, locale=locale) for locale in self.locales
        ]
        for candidate in candidates:
            if candidate.pseudoPosition() is None:
                return str(candidate)
        return str(candidates[0])

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
        processedName = self.glyphNameProcessor(name)
        if marked and processedName not in self.glyphs:
            self.spec.newGlyphs[processedName] = GlyphSpec([])
        return name


def categoryClasses(
    categoryToClasses: dict[str, list[ast.GlyphClassDefinition]],
    locale: LocaleID,
    category: str,
    *glyphClasses: ast.GlyphClassDefinition,
) -> None:
    """Record *glyphClasses* as the class of *category* in *locale*.

    A category class gathers every letter of a category — the vowels of a writing system,
    say, in one position or in all of them. A writing system that writes a category
    differently from the writing systems it shares its letters with is recorded under both
    its own category and the gender-neutral one it is derived from, hence
    `genderNeutralCategory` in `initVariants`.
    """

    categoryToClasses.setdefault(f"{locale}-{category}", []).extend(glyphClasses)


def variantGlyphDescriptor(
    locale: LocaleID,
    alias: str,
    position: JoiningPosition,
    fvs: FVS = 0,
) -> GlyphDescriptor:
    """
    >>> str(variantGlyphDescriptor("MCH", "zr", "fina"))
    'u1877.Jc.medi._fina'
    >>> str(variantGlyphDescriptor("MCHx", "zr", "fina"))
    'u1877.Jc.fina'
    """

    charName = getCharNameByAlias(locale, alias)
    variant = data.variants[charName][position][fvs]
    return GlyphDescriptor.fromData(charName, position, variant, locale=locale)


def _findMemberNames(
    sources: list[GlyphDescriptor],
    writtenTarget: GlyphDescriptor,
) -> list[str]:
    """Find glyph names that compose into *writtenTarget*."""
    # 1) exact match
    for source in sources:
        if source == writtenTarget:
            return [str(source)]
    # 2) match ignoring codePoints
    for source in sources:
        if replace(source, codePoints=[]) == writtenTarget:
            return [str(source)]
    # 3) decompose into written-unit parts
    for writtenVariants in writtenCombinations(writtenTarget.units, writtenTarget.position):
        if len(writtenVariants) == len(writtenTarget.units):
            return ["_" + i for i in writtenVariants]
    raise NotImplementedError(writtenTarget)

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace

from fontTools import unicodedata
from fontTools.feaLib import ast
from tptq.feacomposer import FeaComposer
from ufoLib2.objects import Font, Glyph

from .. import (
    GlyphDescriptor,
    composeGlyph,
    data,
    splitWrittens,
    uNameFromCodePoint,
    writtenCombinations,
)
from ..data import codePointToCmapVariant
from ..data.misc import JoiningPosition, joiningPositions
from ..data.types import FVS, LocaleID
from ..utils import getAliasesByLocale, getCharNameByAlias, namespaceFromLocale


@dataclass
class MongFeaComposer(FeaComposer):
    font: Font | None
    locales: list[LocaleID]
    classes: dict[str, ast.GlyphClassDefinition]
    conditions: dict[str, ast.LookupBlock]
    gdef: dict[str, list]

    def __init__(
        self,
        *,
        font: Font | None,
        locales: list[LocaleID],
    ) -> None:
        self.font = font
        for locale in locales:
            assert locale.removesuffix("x") in locales
        self.locales = locales
        self.classes = {}
        self.conditions = {}
        self.gdef = {}
        super().__init__(
            languageSystems={
                "mong": {"dflt"} | {namespaceFromLocale(i).ljust(4) for i in self.locales}
            }
        )

    def constructPredefinedGlyphs(
        self,
        *,
        initPadding: float = 40,
        finaPadding: float = 100,
    ) -> None:
        assert self.font is not None

        existingCmap = dict[int, Glyph]()
        sources = list[GlyphDescriptor]()
        for name in self.font.keys():
            glyph = self.font[name]
            existingCmap.update((i, glyph) for i in glyph.unicodes)
            try:
                target = GlyphDescriptor.parse(name)
            except:
                continue
            sources.append(target)

        codePointToVariantGlyph = dict[int, Glyph]()
        targetedLocales = {*self.locales}
        for charName, positionToFVSToVariant in data.variants.items():
            variantNames = list[str]()
            for position, fvsToVariant in positionToFVSToVariant.items():
                for variant in fvsToVariant.values():
                    if not targetedLocales.intersection(variant.locales):
                        continue

                    target = GlyphDescriptor.fromData(charName, position, variant)
                    targetName = str(target)
                    variantNames.append(targetName)

                    glyph = self.font.get(self.glyphNameProcessor(targetName))
                    if glyph is not None:
                        continue

                    memberNames: list[str]
                    writtenTarget = replace(target, codePoints=[], suffixes=[])
                    for source in sources:
                        if source == writtenTarget:
                            memberNames = [str(source)]
                            break
                    else:
                        for source in sources:
                            if replace(source, codePoints=[]) == writtenTarget:
                                memberNames = [str(source)]
                                break
                        else:
                            for writtenVariants in writtenCombinations(
                                "".join(writtenTarget.units), writtenTarget.position
                            ):
                                if len(writtenVariants) == len(writtenTarget.units):
                                    memberNames = ["_" + i for i in writtenVariants]
                                    break
                            else:
                                raise NotImplementedError(target)

                    members: list[Glyph | float] = [
                        self.font[self.glyphNameProcessor(i)] for i in memberNames
                    ]
                    if pseudoPosition := target.pseudoPosition():
                        if pseudoPosition in ["isol", "init"]:
                            members = [initPadding, *members]
                        if pseudoPosition in ["isol", "fina"]:
                            members = [*members, finaPadding]
                    composeGlyph(self.font, self.glyphNameProcessor(targetName), members)

            if variantNames:
                codePoint = ord(unicodedata.lookup(charName))
                variant = GlyphDescriptor([codePoint], *codePointToCmapVariant[codePoint])
                codePointToVariantGlyph[codePoint] = self.font[
                    self.glyphNameProcessor(str(variant))
                ]

        for codePoint, variantGlyph in codePointToVariantGlyph.items():
            glyph = composeGlyph(
                self.font, self.glyphNameProcessor(uNameFromCodePoint(codePoint)), [variantGlyph]
            )
            existingGlyph = existingCmap.get(codePoint)
            if existingGlyph is not None:
                existingGlyph.unicodes.remove(codePoint)
            glyph.unicode = codePoint

    def compose(self) -> None:
        from . import ia, ib, iia, iib, iii

        self.initControls()
        self.initVariants()

        ia.compose(self)
        iia.compose(self)
        iii.compose(self)
        iib.compose(self)
        ib.compose(self)

        self.writeGdef()

    def writeGdef(self) -> None:
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

    def initControls(self) -> None:
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
                if self.font is not None:
                    composeGlyph(self.font, self.glyphNameProcessor(variant), [])
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
                if self.font is not None:
                    composeGlyph(self.font, self.glyphNameProcessor(variant), [])
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

        `positionalClass` -- locale + "-" + alias + "." + position, e.g. `@MNG-a.isol`.

        `letterClass` -- locale + "-" + alias, e.g. `@MNG-a`.

        `categoryClass` -- locale + "-" + category (+ "." + position), e.g. `@MNG-vowel` or `@MNG-vowel.init`.

        Initialize condition lookups for variants.

        Conditions generated from `variant.locales` -- locale + "-" + condition, e.g. `MNG-chachlag`.

        In addition, GB shaping requirements result in the need to reset the letter to its default variant. Resetting condition -- locale + "-reset", e.g. `MNG-reset`.
        """

        for locale in self.locales:
            categoryToClasses = dict[str, list[ast.GlyphClassDefinition]]()
            for alias in getAliasesByLocale(locale):
                charName = getCharNameByAlias(locale, alias)
                letter = locale + "-" + alias
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
                            if locale in i.locales
                        ],
                    )
                    self.classes[letter + "." + position] = positionalClass
                    positionalClasses.append(positionalClass)
                    categoryToClasses.setdefault(
                        locale + "-" + genderNeutralCategory + "." + position, []
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
                    categoryToClasses.setdefault(locale + "-" + genderNeutralCategory, []).append(
                        letterClass
                    )
                categoryToClasses.setdefault(locale + "-" + category, []).append(letterClass)

                if lvsPositionalClasses:
                    letterClass = self.namedGlyphClass(letter + "_lvs", lvsPositionalClasses)
                    self.classes[letter + "_lvs"] = letterClass
                    if genderNeutralCategory != category:
                        categoryToClasses.setdefault(
                            locale + "-" + genderNeutralCategory, []
                        ).append(letterClass)
                    categoryToClasses.setdefault(locale + "-" + category, []).append(letterClass)

            for name, positionalClasses in categoryToClasses.items():
                self.classes[name] = self.namedGlyphClass(name, positionalClasses)

        for locale in self.locales:
            for condition in data.locales[locale].conditions:
                with self.Lookup(f"{locale}:{condition}") as lookup:
                    for alias in getAliasesByLocale(locale):
                        charName = getCharNameByAlias(locale, alias)
                        letter = locale + "-" + alias
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
                            self.classes["MNG-" + alias + "." + position],
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
        >>> composer = MongFeaComposer(font=None, locales=["MNG"])
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
        aliases: list[str] = [],
    ) -> ast.GlyphClass:
        """
        >>> composer = MongFeaComposer(font=None, locales=["MNG"])
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
                    for fvs in data.variants[getCharNameByAlias(locale, alias)][position].keys()
                ],
            )
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
                            if (w := variantGlyphDescriptor(locale, alias, position, fvs)).units
                            == splitWrittens(written)
                            and filter(w.units)
                        ]
                    else:
                        variants = []
                        key = f"{locale}-{alias}_lvs.{position}"
                        if key in self.classes:
                            variants = [
                                GlyphDescriptor.parse(g.glyph)
                                for g in self.classes[key].glyphs.glyphs
                                if written in g.glyph
                                and filter(GlyphDescriptor.parse(g.glyph).units)
                            ]
                    glyphs.extend(str(v) for v in variants if str(v) not in glyphs)
        return self.glyphClass(glyphs)

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
        if marked and self.font is not None and name not in self.font:
            composeGlyph(self.font, self.glyphNameProcessor(name), [])
        return name


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

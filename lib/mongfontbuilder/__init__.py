from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Iterable

from fontTools import unicodedata
from ufoLib2.objects import Component, Font, Glyph

from .data import CharacterName, JoiningPosition, LocaleID, VariantData, WrittenUnitID
from .data.misc import fina, init, isol, medi


def constructFont(font: Font, locales: list[LocaleID]) -> None:
    from .otl import MongFeaComposer

    constructGlyphSet(font, locales)

    composer = MongFeaComposer(font, locales)
    assert not font.features.text, font.features.text
    font.features.text = composer.asFeatureFile().asFea()


def parseWrittens(writtens: str | Iterable[str]) -> list[WrittenUnitID]:
    """
    >>> parseWrittens("ABC")
    ['A', 'B', 'C']
    """
    if isinstance(writtens, str):
        return re.sub(r"[A-Z]", lambda x: " " + x[0], writtens).removeprefix(" ").split(" ")
    return list(writtens)


def getPosition(index: int, length: int):
    return isol if length == 1 else (init if index == 0 else fina if index == length - 1 else medi)


def combineWrittens(writtens: str | Iterable[str], position: JoiningPosition) -> list[list[str]]:
    """
    >>> combineWrittens("ABCD", "isol")
    [['A.init', 'B.medi', 'C.medi', 'D.fina'], ['A.init', 'B.medi', 'CD.fina'], ['A.init', 'BC.medi', 'D.fina'], ['A.init', 'BCD.fina'], ['AB.init', 'C.medi', 'D.fina'], ['AB.init', 'CD.fina'], ['ABC.init', 'D.fina'], ['ABCD.isol']]
    """
    parts = list(parseWrittens(writtens) if isinstance(writtens, str) else writtens)

    if "Lv" in parts:
        index = parts.index("Lv")
        if index > 0:
            parts[index - 1] += parts.pop(index)

    leftJoin = 1 if position in (medi, fina) else 0
    rightJoin = 1 if position in (init, medi) else 0
    if leftJoin:
        parts = ["X"] + parts
    if rightJoin:
        parts += ["X"]

    combinations = [[]]
    for part in parts:
        newCombinations = []
        for comb in combinations:
            newCombinations.append(comb + [part])
            if comb:
                newCombinations.append(comb[:-1] + [comb[-1] + part])
        combinations = newCombinations

    results = []
    for comb in combinations:
        result = [
            f"{written}.{getPosition(index, len(comb))}" for index, written in enumerate(comb)
        ][leftJoin : (len(comb) - rightJoin)]
        if (
            len([l for w in result for l in w if l.isupper()])
            == len(list(l for l in str(writtens) if l.isupper()))
            and result
        ):
            results.append(result)
    return results


@dataclass
class GlyphDescriptor:
    codePoints: list[int]
    units: list[WrittenUnitID]
    position: JoiningPosition
    suffixes: list[str] = field(default_factory=list)

    @classmethod
    def parse(cls, name: str) -> GlyphDescriptor:
        """
        >>> GlyphDescriptor.parse('u1820.A.init')
        GlyphDescriptor(codePoints=[6176], units=['A'], position='init', suffixes=[])
        >>> GlyphDescriptor.parse('_A.init')
        GlyphDescriptor(codePoints=[], units=['A'], position='init', suffixes=[])
        """

        x, y, position, *suffixes = (
            "." + name.removeprefix("_")  # _A.init
            if name.startswith("_")
            else name  # u1820.A.init
        ).split(".")
        units = parseWrittens(y)
        assert units and all(i in data.writtenUnits for i in units), name
        assert position in data.types.joiningPositions, name
        instance = cls(
            codePoints=[int(i.removeprefix("u"), 16) for i in x.split("_")] if x else [],
            units=units,
            position=position,
            suffixes=suffixes,
        )
        assert str(instance) == name
        return instance

    @classmethod
    def fromData(
        cls,
        charName: CharacterName,
        position: JoiningPosition,
        variantData: VariantData | None = None,
        suffixes: list[str] = [],
        locale: LocaleID | None = None,
    ) -> GlyphDescriptor:
        from .data import normalizedWritten

        if not variantData:
            variantData = next(i for i in data.variants[charName][position].values() if i.default)

        written = None
        if locale and locale in variantData.locales:
            written = variantData.locales[locale].written
        if not written:
            written = variantData.written
        assert written, variantData

        units, writtenPosition = normalizedWritten(written, data.variants[charName])
        return cls(
            [ord(unicodedata.lookup(charName))],
            units,
            writtenPosition or position,
            (["_" + position] if writtenPosition else []) + suffixes,
        )

    def __str__(self) -> str:
        assert self.units, self
        if self.codePoints:
            name = "_".join(uNameFromCodePoint(i) for i in self.codePoints) + "."
        else:
            name = "_"
        return name + ".".join(["".join(self.units), self.position, *self.suffixes])

    def __add__(self, other: GlyphDescriptor) -> GlyphDescriptor:
        """
        >>> GlyphDescriptor.parse('u1820.A.init') + GlyphDescriptor.parse('u1820.A.medi')
        GlyphDescriptor(codePoints=[6176, 6176], units=['A', 'A'], position='init', suffixes=[])
        """
        joiningType: dict[tuple[JoiningPosition, JoiningPosition], JoiningPosition] = {
            ("init", "fina"): "isol",
            ("init", "medi"): "init",
            ("medi", "medi"): "medi",
            ("medi", "fina"): "fina",
        }
        assert (self.position, other.position) in joiningType
        return GlyphDescriptor(
            self.codePoints + other.codePoints,
            self.units + other.units,
            joiningType[(self.position, other.position)],
        )

    def pseudoPosition(self) -> JoiningPosition | None:
        if self.suffixes:
            suffix = self.suffixes[0]
            if suffix in pseudoPositionSuffixes:
                position = suffix.removeprefix("_")
                assert position in data.misc.joiningPositions
                return position

    def __hash__(self) -> int:
        return hash(self.__str__())


def uNameFromCodePoint(codePoint: int) -> str:
    return f"u{codePoint:04X}"


pseudoPositionSuffixes = ["_" + i for i in data.misc.joiningPositions]


def constructGlyphSet(
    font: Font,
    locales: list[LocaleID],
    *,
    initPadding: float = 40,
    finaPadding: float = 100,
) -> None:
    sources = list[GlyphDescriptor]()
    for name in font.keys():
        try:
            target = GlyphDescriptor.parse(name)
        except:
            continue
        sources.append(target)

    def composeGlyph(name: str, members: list[Glyph | float]) -> Glyph:
        glyph = font.newGlyph(name)
        for member in members:
            if isinstance(member, Glyph):
                component = Component(name)
                component.move((glyph.width, 0))
                glyph.components.append(component)
                glyph.width += member.width
            else:
                glyph.width += member
        return glyph

    targetedLocales = {*locales}
    for charName, positionToFVSToVariant in data.variants.items():
        variantNames = list[str]()
        for position, fvsToVariant in positionToFVSToVariant.items():
            for fvs, variant in fvsToVariant.items():
                if not targetedLocales.intersection(variant.locales):
                    continue

                target = GlyphDescriptor.fromData(charName, position, variant)
                targetName = str(target)
                variantNames.append(targetName)

                glyph = font.get(targetName)
                if glyph is not None:
                    glyph.unicode = None
                    continue

                idealSource = replace(target, codePoints=[], suffixes=[])
                for source in sources:
                    if source == idealSource:
                        break
                else:
                    for source in sources:
                        if replace(source, codePoints=[]) == idealSource:
                            break
                    else:
                        raise StopIteration(idealSource)
                composeGlyph(
                    targetName,
                    [
                        initPadding if target.pseudoPosition() in ["isol", "init"] else 0,
                        font[str(source)],
                        finaPadding if target.pseudoPosition() in ["isol", "fina"] else 0,
                    ],
                )

        if variantNames:
            codePoint = ord(unicodedata.lookup(charName))
            glyph = composeGlyph(uNameFromCodePoint(codePoint), [])  # FIXME
            glyph.unicode = codePoint

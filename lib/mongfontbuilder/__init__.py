from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Iterable

from fontTools import unicodedata
from fontTools.misc.transform import Identity

from .data import (
    CharacterName,
    JoiningPosition,
    LocaleID,
    VariantData,
    VariantReference,
    WrittenUnitID,
)
from .data.misc import fina, init, isol, medi


def splitWrittens(writtens: str | Iterable[str]) -> list[WrittenUnitID]:
    """
    >>> splitWrittens("ABbCcc")
    ['A', 'Bb', 'Ccc']
    """

    if isinstance(writtens, str):
        return re.sub(r"[A-Z]", lambda x: " " + x[0], writtens).removeprefix(" ").split(" ")
    return list(writtens)


def getPosition(index: int, length: int) -> JoiningPosition:
    return isol if length == 1 else (init if index == 0 else fina if index == length - 1 else medi)


def writtenCombinations(writtens: str, position: JoiningPosition) -> Iterator[list[str]]:
    """
    >>> [*writtenCombinations("ABCD", "isol")]
    [['A.init', 'B.medi', 'C.medi', 'D.fina'], ['A.init', 'B.medi', 'CD.fina'], ['A.init', 'BC.medi', 'D.fina'], ['A.init', 'BCD.fina'], ['AB.init', 'C.medi', 'D.fina'], ['AB.init', 'CD.fina'], ['ABC.init', 'D.fina'], ['ABCD.isol']]
    """

    parts = splitWrittens(writtens)
    if "Lv" in parts:
        index = parts.index("Lv")
        if index > 0:
            parts[index - 1] += parts.pop(index)

    leftJoin = 1 if position in (medi, fina) else 0
    rightJoin = 1 if position in (init, medi) else 0
    placeholder = "X"
    if leftJoin:
        parts = [placeholder] + parts
    if rightJoin:
        parts += [placeholder]

    combinations = [[]]
    for part in parts:
        newCombinations = []
        for comb in combinations:
            newCombinations.append(comb + [part])
            if comb:
                newCombinations.append(comb[:-1] + [comb[-1] + part])
        combinations = newCombinations

    for comb in combinations:
        result = [
            f"{written}.{getPosition(index, len(comb))}" for index, written in enumerate(comb)
        ][leftJoin : (len(comb) - rightJoin)]
        if (
            len([l for w in result for l in w if l.isupper()])
            == len(list(l for l in str(writtens) if l.isupper()))
            and result
        ):
            yield result


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
        units = splitWrittens(y)
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
        from .data import variantFromReference

        if not variantData:
            variantData = next(i for i in data.variants[charName][position].values() if i.default)

        written = None
        if locale and locale in variantData.locales:
            written = variantData.locales[locale].written
        if not written:
            written = variantData.written
        assert written, variantData

        if isinstance(written, VariantReference):
            units = variantFromReference(written, data.variants[charName])
            suffixes = ["_" + position, *suffixes]
            position = written.position
        else:
            units = written
        return cls([ord(unicodedata.lookup(charName))], units, position, suffixes)

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

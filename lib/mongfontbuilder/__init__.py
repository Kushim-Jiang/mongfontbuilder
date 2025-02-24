from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from importlib.resources import files

import yaml
from fontTools import unicodedata
from fontTools.feaLib.ast import FeatureFile
from fontTools.feaLib.parser import Parser
from ufoLib2.objects import Component, Font, Glyph

import data

from .data import JoiningPosition, WrittenUnitID
from .data.types import CharacterName, VariantData


def constructFont(font: Font) -> None:
    constructGlyphSet(font)
    font.features.text = makeFeatureFile(availableGlyphs=font.keys()).asFea()


def makeFeatureFile(availableGlyphs: Iterable[str] = ()) -> FeatureFile:
    """
    Specify `availableGlyphs` to validate the glyph set against the feature file’s requirement.
    An empty set is ignored by `Parser`.
    """

    assert __package__
    path = files(__package__) / "otl" / "main.fea"
    with path.open(encoding="utf-8") as f:
        return Parser(featurefile=f, glyphNames=availableGlyphs).parse()


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
        units = re.sub(r"[A-Z]", lambda x: " " + x[0], y).removeprefix(" ").split(" ")
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
    ) -> GlyphDescriptor:
        from .data import normalizedWritten

        if not variantData:
            variantData = next(i for i in data.variants[charName][position].values() if i.default)
        units, writtenPosition = normalizedWritten(variantData.written, data.variants[charName])
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


def uNameFromCodePoint(codePoint: int) -> str:
    return f"u{codePoint:04X}"


pseudoPositionSuffixes = ["_" + i for i in data.misc.joiningPositions]


def constructGlyphSet(font: Font, initPadding: float = 40, finaPadding: float = 100) -> None:
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

    for charName in data.variants:
        codePoint = ord(unicodedata.lookup(charName))
        glyph = composeGlyph(uNameFromCodePoint(codePoint), [])  # FIXME
        glyph.unicode = codePoint

    categoryToExpectedGlyphs = dict[str, list[str]]()
    for path in (data.dir / "glyphs").iterdir():
        if path.name.endswith(".yaml"):
            with path.open(encoding="utf-8") as f:
                categoryToExpectedGlyphs[path.name] = [*yaml.safe_load(f)]

    for name in categoryToExpectedGlyphs["empty.yaml"]:
        composeGlyph(name, [])

    for name in categoryToExpectedGlyphs["variants.yaml"]:
        glyph = font.get(name)
        if glyph is not None:
            glyph.unicode = None
            continue
        target = GlyphDescriptor.parse(name)
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
            name,
            [
                initPadding if target.pseudoPosition() in ["isol", "init"] else 0,
                font[str(source)],
                finaPadding if target.pseudoPosition() in ["isol", "fina"] else 0,
            ],
        )

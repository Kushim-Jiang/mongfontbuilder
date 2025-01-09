from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, replace
from importlib.resources import files

import yaml
from fontTools import unicodedata
from fontTools.feaLib.ast import FeatureFile
from fontTools.feaLib.parser import Parser
from ufoLib2.objects import Component, Font, Glyph

import data

from .data import JoiningPosition, WrittenUnitID


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
    writtenUnits: list[WrittenUnitID]
    joiningPosition: JoiningPosition
    suffixes: list[str]

    @classmethod
    def parse(cls, name: str) -> GlyphDescriptor:
        """
        >>> GlyphDescriptor.parse('u1820.A.init')
        GlyphDescriptor(codePoints=[6176], writtenUnits=['A'], joiningPosition='init', suffixes=[])
        >>> GlyphDescriptor.parse('_A.init')
        GlyphDescriptor(codePoints=[], writtenUnits=['A'], joiningPosition='init', suffixes=[])
        """

        x, y, joiningPosition, *suffixes = (
            "." + name.removeprefix("_")  # _A.init
            if name.startswith("_")
            else name  # u1820.A.init
        ).split(".")
        writtenUnits = re.sub(r"[A-Z]", lambda x: " " + x[0], y).removeprefix(" ").split(" ")
        assert writtenUnits and all(i in data.writtenUnits for i in writtenUnits), name
        assert joiningPosition in data.types.joiningPositions, name
        instance = cls(
            codePoints=[int(i.removeprefix("u"), 16) for i in x.split("_")] if x else [],
            writtenUnits=writtenUnits,
            joiningPosition=joiningPosition,
            suffixes=suffixes,
        )
        assert str(instance) == name
        return instance

    def __str__(self) -> str:
        assert self.writtenUnits, self
        if self.codePoints:
            name = "_".join(f"u{i:04X}" for i in self.codePoints) + "."
        else:
            name = "_"
        return name + ".".join(["".join(self.writtenUnits), self.joiningPosition, *self.suffixes])

    def pseudoPosition(self) -> JoiningPosition | None:
        if self.suffixes:
            suffix = self.suffixes[0]
            if suffix in pseudoPositionSuffixes:
                position = suffix.removeprefix("_")
                assert position in data.misc.joiningPositions
                return position


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
        glyph = composeGlyph(f"u{codePoint:04X}", [])  # FIXME
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

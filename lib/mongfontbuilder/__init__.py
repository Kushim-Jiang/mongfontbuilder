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
class VariantName:
    codePoints: list[int]
    writtenUnits: list[WrittenUnitID]
    joiningPosition: JoiningPosition
    suffixes: list[str]

    @classmethod
    def parse(cls, string: str) -> VariantName:
        x, y, joiningPosition, *suffixes = string.split(".")
        writtenUnits = re.sub(r"[A-Z]", lambda x: " " + x[0], y).removeprefix(" ").split(" ")
        assert writtenUnits and all(i in data.writtenUnits for i in writtenUnits), string
        assert joiningPosition in data.types.joiningPositions, string
        return cls(
            codePoints=[] if x == "_" else [int(i.removeprefix("u"), 16) for i in x.split("_")],
            writtenUnits=writtenUnits,
            joiningPosition=joiningPosition,
            suffixes=suffixes,
        )

    def string(self) -> str:
        assert self.writtenUnits, self
        return ".".join(
            [
                "_".join(f"u{i:04X}" for i in self.codePoints) or "_",
                "".join(self.writtenUnits),
                self.joiningPosition,
                *self.suffixes,
            ]
        )


def constructGlyphSet(font: Font, initPadding: float = 40, finaPadding: float = 100) -> None:
    categoryToExpectedGlyphs = dict[str, list[str]]()
    for path in (data.dir / "glyphs").iterdir():
        if path.name.endswith(".yaml"):
            with path.open(encoding="utf-8") as f:
                categoryToExpectedGlyphs[path.name] = [*yaml.safe_load(f)]

    existingNameToVariant = dict[str, VariantName]()
    for name in font.keys():
        try:
            variant = VariantName.parse(name)
        except:
            continue
        existingNameToVariant[name] = variant

    font.glyphOrder = []

    for charName in data.variants:
        codePoint = ord(unicodedata.lookup(charName))
        name = f"u{codePoint:04X}"
        glyph = composeGlyph([])  # FIXME
        glyph.unicode = codePoint
        font[name] = glyph
        font.glyphOrder.append(name)

    pseudoPositionSuffixes = ["_" + i for i in data.constants.joiningPositions]

    for expectedName in categoryToExpectedGlyphs["variants.yaml"]:
        font.glyphOrder.append(expectedName)
        glyph = font.get(expectedName)
        if glyph is not None:
            glyph.unicode = None
            continue

        expectedVariant = VariantName.parse(expectedName)
        pseudoPosition: JoiningPosition | None = None
        if expectedVariant.suffixes:
            suffix = expectedVariant.suffixes[0]
            if suffix in pseudoPositionSuffixes:
                position = suffix.removeprefix("_")
                assert position in data.constants.joiningPositions
                pseudoPosition = position

        idealVariant = replace(expectedVariant, codePoints=[], suffixes=[])
        for name, variant in existingNameToVariant.items():
            if variant == idealVariant:
                break
        else:
            for name, variant in existingNameToVariant.items():
                if replace(variant, codePoints=[]) == idealVariant:
                    break
            else:
                raise StopIteration(idealVariant)

        font[expectedName] = composeGlyph(
            [
                initPadding if pseudoPosition in ["isol", "init"] else 0,
                font[name],
                finaPadding if pseudoPosition in ["isol", "fina"] else 0,
            ]
        )

    for name in categoryToExpectedGlyphs["empty.yaml"]:
        font[name] = composeGlyph([])
        font.glyphOrder.append(name)


def composeGlyph(members: list[Glyph | float]) -> Glyph:
    glyph = Glyph()
    for member in members:
        if isinstance(member, Glyph):
            assert member.name
            component = Component(member.name)
            component.move((glyph.width, 0))
            glyph.components.append(component)
            glyph.width += member.width
        else:
            glyph.width += member
    return glyph

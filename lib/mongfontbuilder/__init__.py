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
class GlyphIdentity:
    codePoints: list[int]
    writtenUnits: list[WrittenUnitID]
    joiningPosition: JoiningPosition
    suffixes: list[str]

    @classmethod
    def parse(cls, name: str) -> GlyphIdentity:
        x, y, joiningPosition, *suffixes = name.split(".")
        writtenUnits = re.sub(r"[A-Z]", lambda x: " " + x[0], y).removeprefix(" ").split(" ")
        assert writtenUnits and all(i in data.writtenUnits for i in writtenUnits), name
        assert joiningPosition in data.types.joiningPositions, name
        return cls(
            codePoints=[] if x == "_" else [int(i.removeprefix("u"), 16) for i in x.split("_")],
            writtenUnits=writtenUnits,
            joiningPosition=joiningPosition,
            suffixes=suffixes,
        )

    def __str__(self) -> str:
        assert self.writtenUnits, self
        return ".".join(
            [
                "_".join(f"u{i:04X}" for i in self.codePoints) or "_",
                "".join(self.writtenUnits),
                self.joiningPosition,
                *self.suffixes,
            ]
        )

    def pseudoPosition(self) -> JoiningPosition | None:
        if self.suffixes:
            suffix = self.suffixes[0]
            if suffix in pseudoPositionSuffixes:
                position = suffix.removeprefix("_")
                assert position in data.misc.joiningPositions
                return position


pseudoPositionSuffixes = ["_" + i for i in data.misc.joiningPositions]


def constructGlyphSet(font: Font, initPadding: float = 40, finaPadding: float = 100) -> None:
    existingNameToIdentity = dict[str, GlyphIdentity]()
    for name in font.keys():
        try:
            existingIdentity = GlyphIdentity.parse(name)
        except:
            continue
        existingNameToIdentity[name] = existingIdentity

    def composeGlyph(name: str, members: list[str | float]) -> Glyph:
        glyph = font.newGlyph(name)
        for member in members:
            if isinstance(member, str):
                component = Component(name)
                component.move((glyph.width, 0))
                glyph.components.append(component)
                glyph.width += font[member].width
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

        identity = GlyphIdentity.parse(name)
        idealIdentity = replace(identity, codePoints=[], suffixes=[])
        for existingName, existingIdentity in existingNameToIdentity.items():
            if existingIdentity == idealIdentity:
                break
        else:
            for existingName, existingIdentity in existingNameToIdentity.items():
                if replace(existingIdentity, codePoints=[]) == idealIdentity:
                    break
            else:
                raise StopIteration(idealIdentity)
        composeGlyph(
            name,
            [
                initPadding if identity.pseudoPosition() in ["isol", "init"] else 0,
                existingName,
                finaPadding if identity.pseudoPosition() in ["isol", "fina"] else 0,
            ],
        )
